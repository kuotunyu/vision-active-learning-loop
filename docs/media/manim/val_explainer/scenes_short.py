"""The 30-second README explainer. Five segments; each takes (scene, ctx, ...) and can be re-sequenced."""

from __future__ import annotations

import random
from dataclasses import dataclass

from manim import (
    DOWN,
    LEFT,
    PI,
    RIGHT,
    UP,
    Arrow,
    Axes,
    ChangeDecimalToValue,
    Create,
    FadeIn,
    FadeOut,
    Indicate,
    Integer,
    LaggedStart,
    Polygon,
    Rectangle,
    Scene,
    Square,
    SurroundingRectangle,
    Text,
    VGroup,
    Write,
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


# ------------------------------------------------------------------ loop

FLY_PER_ROUND = 14  # representative squares that visibly fly per lane per round
SHADE_COUNT = 400  # pool squares that visibly take an uncertainty shade during scoring
ROUND_KEYS = ("0.05", "0.10", "0.20")
LANE_ARMS = ("random", "entropy", "margin")


@dataclass
class LaneSet:
    lanes: dict[str, VGroup]
    counters: dict[str, Integer]
    caption: Text


def digits_class(font: str) -> type[Text]:
    """A Text subclass with the font baked in, so DecimalNumber renders digits without LaTeX."""

    class Digits(Text):
        def __init__(self, string: str, **kwargs) -> None:
            kwargs.setdefault("font", font)
            super().__init__(string, **kwargs)

    return Digits


def _lane(ctx: Context, arm: str, width: float, height: float) -> tuple[VGroup, Integer]:
    color = ctx.style.colors[arm]
    box = Rectangle(width=width, height=height, stroke_color=color, stroke_width=3, fill_color=color, fill_opacity=0.08)
    name = text(ctx, f"lane_{arm}", "label", color).next_to(box.get_left(), RIGHT, buff=0.2)
    counter = Integer(
        ctx.data.start_count(),
        mob_class=digits_class(ctx.style.font),
        font_size=ctx.style.sizes["counter"],
        color=ctx.style.colors["text"],
    )
    counter.next_to(box.get_right(), LEFT, buff=0.3)
    return VGroup(box, name, counter), counter


def loop_segment(scene: Scene, ctx: Context, layout: PoolLayout, fade_out: bool = True) -> LaneSet:
    style = ctx.style
    data = ctx.data
    pool_label, test_label, start_label = layout.labels
    test_group = VGroup(layout.test, layout.test_box)

    # compact the pool and the test set to make room for the lanes
    scene.play(
        layout.pool.animate.scale(0.72).to_edge(LEFT, buff=0.4).shift(UP * 0.3),
        FadeOut(pool_label),
        FadeOut(start_label),
        test_group.animate.scale(0.5).to_corner(DOWN + RIGHT, buff=0.8),
        FadeOut(test_label),
        run_time=0.8,
    )
    test_label.scale(0.75).next_to(layout.test_box, DOWN, buff=0.08).align_to(layout.test_box, RIGHT)
    scene.add(test_label)

    lanes: dict[str, VGroup] = {}
    counters: dict[str, Integer] = {}
    stack = VGroup()
    for arm in LANE_ARMS:
        lane, counter = _lane(ctx, arm, width=4.6, height=0.9)
        lanes[arm] = lane
        counters[arm] = counter
        stack.add(lane)
    stack.arrange(DOWN, buff=0.35).next_to(layout.pool, RIGHT, buff=0.9).align_to(layout.pool, UP)

    score_label = text(ctx, "score", "small", style.colors["muted"]).next_to(stack, UP, buff=0.15)
    retrain_arrow = Arrow(
        stack.get_right() + RIGHT * 0.1, stack.get_right() + RIGHT * 1.1,
        buff=0, color=style.colors["muted"], stroke_width=3,
    )
    retrain = text(ctx, "retrain", "small", style.colors["muted"]).next_to(retrain_arrow, UP, buff=0.1)
    evaluate = text(ctx, "evaluate", "small", style.colors["muted"]).next_to(layout.test_box, UP, buff=0.12)
    eval_arrow = Arrow(
        retrain_arrow.get_end(), evaluate.get_top() + UP * 0.05,
        buff=0.05, color=style.colors["muted"], stroke_width=3,
    )
    caption = text(ctx, "loop_caption", "caption").to_corner(DOWN + LEFT, buff=0.35)

    scene.play(LaggedStart(*[FadeIn(lane, shift=RIGHT * 0.2) for lane in stack], lag_ratio=0.2), run_time=0.9)
    scene.play(
        FadeIn(score_label), FadeIn(retrain_arrow), FadeIn(retrain), FadeIn(eval_arrow), FadeIn(evaluate),
        run_time=0.6,
    )

    picker = random.Random(START_SEED + 1)
    start = set(layout.start_indices)
    unlabeled = [i for i in range(data.pool_size) if i not in start]

    def one_round(key: str, run_time: float, show_scoring: bool) -> None:
        target = data.budgets[key]
        shade: list[int] = []
        if show_scoring:
            # uncertainty shading: entropy/margin lanes act on scores; random ignores them
            shade = picker.sample(unlabeled, min(len(unlabeled), SHADE_COUNT))
            scene.play(
                LaggedStart(
                    *[
                        layout.pool[i].animate.set_fill(style.colors["margin"], opacity=0.35 + 0.65 * picker.random())
                        for i in shade
                    ],
                    lag_ratio=0.002,
                ),
                Indicate(score_label, color=style.colors["margin"]),
                run_time=run_time * 0.35,
            )
        ghosts: list[Square] = []
        flights = []
        for arm in LANE_ARMS:
            box = lanes[arm][0]
            for i in picker.sample(unlabeled, FLY_PER_ROUND):
                ghost = layout.pool[i].copy().set_fill(style.colors[arm], opacity=1.0)
                target_point = box.get_center() + RIGHT * picker.uniform(-0.9, 0.9) + UP * picker.uniform(-0.22, 0.22)
                ghosts.append(ghost)
                flights.append(ghost.animate.move_to(target_point).scale(1.6))
        scene.add(*ghosts)
        scene.play(
            LaggedStart(*flights, lag_ratio=0.01),
            *[ChangeDecimalToValue(counters[arm], target) for arm in LANE_ARMS],
            run_time=run_time * 0.4,
        )
        scene.play(
            FadeOut(VGroup(*ghosts)),
            Indicate(retrain, color=style.colors["text"]),
            Indicate(retrain_arrow, color=style.colors["text"]),
            run_time=run_time * 0.12,
        )
        scene.play(
            Indicate(evaluate, color=style.colors["text"]),
            Indicate(eval_arrow, color=style.colors["text"]),
            run_time=run_time * 0.13,
        )
        if shade:
            scene.play(
                *[layout.pool[i].animate.set_fill(style.colors["pool"], opacity=1.0) for i in shade],
                run_time=0.2,
            )

    one_round(ROUND_KEYS[0], run_time=3.6, show_scoring=True)
    scene.play(FadeIn(caption), run_time=0.3)
    one_round(ROUND_KEYS[1], run_time=1.4, show_scoring=False)
    one_round(ROUND_KEYS[2], run_time=1.4, show_scoring=False)
    scene.wait(0.5)

    lane_set = LaneSet(lanes=lanes, counters=counters, caption=caption)
    if fade_out:
        scene.play(FadeOut(*scene.mobjects), run_time=0.5)
    return lane_set


# ------------------------------------------------------------------ curve

X_TICKS = {0.02: "2%", 0.05: "5%", 0.10: "10%", 0.20: "20%"}


def _tick(ctx: Context, label: str) -> Text:
    return Text(label, font=ctx.style.font, font_size=ctx.style.sizes["small"], color=ctx.style.colors["muted"])


def _axes(ctx: Context, y_max: float) -> Axes:
    step = 0.01 if y_max <= 0.05 else 0.02
    small = ctx.style.sizes["small"]
    axes = Axes(
        x_range=[0, 0.22, 0.05],
        y_range=[0, y_max, step],
        x_length=6.4,
        y_length=4.0,
        tips=False,
        axis_config={"include_numbers": False, "stroke_color": ctx.style.colors["muted"]},
    )
    axes.x_axis.add_labels({x: _tick(ctx, label) for x, label in X_TICKS.items()}, font_size=small)
    y_labels = {}
    value = step
    while value <= y_max + 1e-9:
        y_labels[value] = _tick(ctx, f"{value:.2f}")
        value = round(value + step, 6)
    axes.y_axis.add_labels(y_labels, font_size=small)
    return axes


def _line(axes: Axes, points: list[tuple[float, float]], color: str, width: float, opacity: float = 1.0):
    graph = axes.plot_line_graph(
        x_values=[p[0] for p in points],
        y_values=[p[1] for p in points],
        line_color=color,
        stroke_width=width,
        add_vertex_dots=True,
        vertex_dot_radius=0.05,
        vertex_dot_style={"fill_color": color},
    )
    graph.set_opacity(opacity)
    return graph


def curve_segment(scene: Scene, ctx: Context, fade_out: bool = True) -> None:
    style = ctx.style
    data = ctx.data
    first, *others = data.seeds
    y_max = max(p[1] for seed in data.seeds for arm in ("random", "margin") for p in data.curves[seed][arm]) * 1.15
    y_max = round(y_max + 0.005, 2)
    axes = _axes(ctx, y_max).to_edge(LEFT, buff=0.7).shift(UP * 0.2)
    x_label = text(ctx, "axis_x", "small", style.colors["muted"]).next_to(axes.x_axis, DOWN, buff=0.45)
    y_label = text(ctx, "axis_y", "small", style.colors["muted"]).rotate(PI / 2).next_to(axes.y_axis, LEFT, buff=0.35)
    scene.play(Create(axes), FadeIn(x_label), FadeIn(y_label), run_time=0.8)

    rand = _line(axes, data.curves[first]["random"], style.colors["random"], 4)
    marg = _line(axes, data.curves[first]["margin"], style.colors["margin"], 4)
    scene.play(Create(rand), run_time=1.0)
    scene.play(Create(marg), run_time=1.0)

    forward = [axes.c2p(x, y) for x, y in data.curves[first]["margin"]]
    backward = [axes.c2p(x, y) for x, y in reversed(data.curves[first]["random"])]
    area = Polygon(*forward, *backward, fill_color=style.colors["margin"], fill_opacity=0.3, stroke_width=0)

    panel = VGroup(text(ctx, "delta_title", "label", style.colors["margin"]))
    lines = {seed: text(ctx, f"delta_seed_{seed}", "label") for seed in data.seeds}
    for seed in data.seeds:
        panel.add(lines[seed])
    sign = text(ctx, "sign", "label", style.colors["start"])
    note = text(ctx, "range_note", "small", style.colors["muted"])
    panel.add(sign, note)
    panel.arrange(DOWN, aligned_edge=LEFT, buff=0.22).to_edge(RIGHT, buff=0.6).shift(UP * 0.2)

    scene.play(FadeIn(area), FadeIn(panel[0]), Write(lines[first]), run_time=1.2)
    scene.wait(0.4)
    for seed in others:
        thin_r = _line(axes, data.curves[seed]["random"], style.colors["random"], 2, opacity=0.55)
        thin_m = _line(axes, data.curves[seed]["margin"], style.colors["margin"], 2, opacity=0.55)
        scene.play(Create(thin_r), Create(thin_m), Write(lines[seed]), run_time=1.1)
    scene.play(FadeIn(sign, shift=UP * 0.1), run_time=0.5)
    scene.play(FadeIn(note), run_time=0.4)
    scene.wait(1.6)
    if fade_out:
        scene.play(FadeOut(*scene.mobjects), run_time=0.5)


# ------------------------------------------------------------------ scenes


class TitleSegment(Scene):
    def construct(self) -> None:
        title_segment(self, make_context(), fade_out=False)


class PoolSegment(Scene):
    def construct(self) -> None:
        ctx = make_context()
        pool_segment(self, ctx, build_pool_layout(ctx))


class LoopSegment(Scene):
    def construct(self) -> None:
        ctx = make_context()
        layout = build_pool_layout(ctx)
        self.add(layout.pool, layout.test, layout.test_box, layout.labels)
        for i in layout.start_indices:
            layout.pool[i].set_fill(ctx.style.colors["start"])
        loop_segment(self, ctx, layout, fade_out=False)


class CurveSegment(Scene):
    def construct(self) -> None:
        curve_segment(self, make_context(), fade_out=False)


class ValLoopShort(Scene):
    def construct(self) -> None:
        ctx = make_context()
        title_segment(self, ctx)
        layout = build_pool_layout(ctx)
        pool_segment(self, ctx, layout)
        loop_segment(self, ctx, layout)
        curve_segment(self, ctx)
