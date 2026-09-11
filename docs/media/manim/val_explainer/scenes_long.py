"""The long portfolio explainer: the short segments, three chapters, a closing card."""

from __future__ import annotations

from dataclasses import dataclass

from manim import (
    DOWN,
    LEFT,
    RIGHT,
    UP,
    Create,
    DashedLine,
    Dot,
    FadeIn,
    FadeOut,
    GrowFromEdge,
    LaggedStart,
    Polygon,
    Rectangle,
    ReplacementTransform,
    Scene,
    Text,
    Transform,
    VGroup,
)

from val_explainer.copy import render_copy_long
from val_explainer.data import ARMS, BUDGET_KEYS, ExplainerData, RulePair, load_rule_pair
from val_explainer.scenes_short import (
    MAX_TEXT_WIDTH,
    X_TICKS,
    Context,
    _axes,
    _line,
    _tick,
    build_pool_layout,
    curve_segment,
    loop_segment,
    make_context,
    pool_segment,
    title_segment,
)
from val_explainer.style import Style


@dataclass
class LongContext:
    pair: RulePair
    copy: dict[str, str]
    style: Style
    short: Context


def make_long_context() -> LongContext:
    short = make_context()
    pair = load_rule_pair()
    return LongContext(pair=pair, copy=render_copy_long(pair), style=short.style, short=short)


def text_long(ctx: LongContext, key: str, size: str = "label", color: str | None = None) -> Text:
    mobject = Text(
        ctx.copy[key],
        font=ctx.style.font,
        font_size=ctx.style.sizes[size],
        color=color or ctx.style.colors["text"],
    )
    if mobject.width > MAX_TEXT_WIDTH:
        mobject.scale_to_fit_width(MAX_TEXT_WIDTH)
    return mobject


def chapter_card(scene: Scene, ctx: LongContext, title_key: str, sub_key: str) -> None:
    title = text_long(ctx, title_key, "title")
    sub = text_long(ctx, sub_key, "sub", ctx.style.colors["muted"]).next_to(title, DOWN, buff=0.4)
    scene.play(FadeIn(title, shift=UP * 0.2), FadeIn(sub), run_time=0.7)
    scene.wait(1.3)
    scene.play(FadeOut(title), FadeOut(sub), run_time=0.4)


# ------------------------------------------------------------------ chapter 1: two training-length rules

BAR_WIDTH = 1.3
BAR_MAX_HEIGHT = 3.0


def _bars(ctx: LongContext) -> tuple[VGroup, VGroup, VGroup]:
    """Four budget bars (images), their tick labels, and image-count labels."""
    b = ctx.pair.rule_b
    biggest = max(b.budgets.values())
    bars, ticks, counts = VGroup(), VGroup(), VGroup()
    for key in BUDGET_KEYS:
        height = max(BAR_MAX_HEIGHT * b.budgets[key] / biggest, 0.18)
        bar = Rectangle(
            width=BAR_WIDTH, height=height,
            fill_color=ctx.style.colors["pool"], fill_opacity=1.0, stroke_width=0,
        )
        bars.add(bar)
    bars.arrange(RIGHT, buff=1.0, aligned_edge=DOWN).move_to(DOWN * 0.7)
    for key, bar in zip(BUDGET_KEYS, bars):
        ticks.add(_tick(ctx.short, X_TICKS[float(key)]).next_to(bar, DOWN, buff=0.15))
        count = Text(
            ctx.copy[f"bar_images_{key}"],
            font=ctx.style.font, font_size=ctx.style.sizes["small"], color=ctx.style.colors["muted"],
        )
        counts.add(count.next_to(bar, DOWN, buff=0.45))
    return bars, ticks, counts


def _epoch_labels(ctx: LongContext, bars: VGroup, prefix: str, color: str) -> VGroup:
    labels = VGroup()
    for key, bar in zip(BUDGET_KEYS, bars):
        label = Text(ctx.copy[f"{prefix}_{key}"], font=ctx.style.font, font_size=ctx.style.sizes["label"], color=color)
        labels.add(label.next_to(bar, UP, buff=0.15))
    return labels


def arm_legend(ctx: LongContext) -> VGroup:
    """One row: coloured dot + arm name for the three arms (names come from the short copy)."""
    items = VGroup()
    for arm in ARMS:
        dot = Dot(radius=0.09, color=ctx.style.colors[arm])
        name = Text(
            ctx.short.copy[f"lane_{arm}"],
            font=ctx.style.font, font_size=ctx.style.sizes["small"], color=ctx.style.colors[arm],
        ).next_to(dot, RIGHT, buff=0.12)
        items.add(VGroup(dot, name))
    return items.arrange(RIGHT, buff=0.6)


def _mini_axes(ctx: LongContext, data: ExplainerData, title_key: str, sign_key: str) -> VGroup:
    """A small three-arm mean-curve panel with its rule title and sign line."""
    y_max = round(max(p[1] for arm in ARMS for p in data.mean_curve[arm]) * 1.2 + 0.005, 2)
    axes = _axes(ctx.short, y_max)
    lines = VGroup(*[_line(axes, data.mean_curve[arm], ctx.style.colors[arm], 3) for arm in ARMS])
    title = text_long(ctx, title_key, "label").next_to(axes, UP, buff=0.3)
    sign = text_long(ctx, sign_key, "small", ctx.style.colors["start"]).next_to(axes, DOWN, buff=0.55)
    return VGroup(axes, lines, title, sign).scale(0.62)


def chapter_rules_segment(scene: Scene, ctx: LongContext, fade_out: bool = True) -> None:
    style = ctx.style
    chapter_card(scene, ctx, "ch1_title", "ch1_sub")

    bars, ticks, counts = _bars(ctx)
    epochs_a = _epoch_labels(ctx, bars, "bar_epochs_a", style.colors["start"])
    rule_a = text_long(ctx, "ch1_rule_a", "label").to_edge(UP, buff=0.5)
    rule_a_note = text_long(ctx, "ch1_rule_a_epochs", "caption", style.colors["muted"]).next_to(rule_a, DOWN, buff=0.2)
    computed = text_long(ctx, "ch1_computed", "small", style.colors["muted"]).to_corner(DOWN + RIGHT, buff=0.35)
    scene.play(FadeIn(rule_a), FadeIn(rule_a_note), run_time=0.5)
    scene.play(
        LaggedStart(*[GrowFromEdge(bar, DOWN) for bar in bars], lag_ratio=0.15),
        FadeIn(ticks), FadeIn(counts),
        run_time=1.0,
    )
    scene.play(LaggedStart(*[FadeIn(label, shift=UP * 0.1) for label in epochs_a], lag_ratio=0.15), FadeIn(computed), run_time=0.9)
    scene.wait(1.8)

    steps_b = _epoch_labels(ctx, bars, "bar_steps_b", style.colors["text"])
    epochs_b = _epoch_labels(ctx, bars, "bar_epochs_b", style.colors["start"])
    for step_label, epoch_label in zip(steps_b, epochs_b):
        epoch_label.next_to(step_label, UP, buff=0.08)
    rule_b = text_long(ctx, "ch1_rule_b", "label").to_edge(UP, buff=0.5)
    rule_b_note = text_long(ctx, "ch1_rule_b_note", "caption", style.colors["muted"]).next_to(rule_b, DOWN, buff=0.2)
    scene.play(
        ReplacementTransform(rule_a, rule_b),
        ReplacementTransform(rule_a_note, rule_b_note),
        *[ReplacementTransform(old, new) for old, new in zip(epochs_a, epochs_b)],
        FadeIn(steps_b),
        FadeOut(computed),
        run_time=1.0,
    )
    scene.wait(2.0)

    scene.play(
        FadeOut(bars), FadeOut(ticks), FadeOut(counts), FadeOut(epochs_b), FadeOut(steps_b),
        FadeOut(rule_b), FadeOut(rule_b_note),
        run_time=0.5,
    )
    panel_a = _mini_axes(ctx, ctx.pair.rule_a, "ch1_axis_a", "ch1_sign_a")
    panel_b = _mini_axes(ctx, ctx.pair.rule_b, "ch1_axis_b", "ch1_sign_b")
    VGroup(panel_a, panel_b).arrange(RIGHT, buff=0.8).move_to(UP * 0.4)
    legend = arm_legend(ctx).to_edge(UP, buff=0.35)
    both = text_long(ctx, "ch1_both", "caption").to_edge(DOWN, buff=0.75)
    fair = text_long(ctx, "ch1_fair", "small", style.colors["muted"]).next_to(both, DOWN, buff=0.15)
    scene.play(Create(panel_a[0]), Create(panel_b[0]), FadeIn(panel_a[2]), FadeIn(panel_b[2]), FadeIn(legend), run_time=0.8)
    scene.play(Create(panel_a[1]), Create(panel_b[1]), run_time=1.2)
    scene.play(FadeIn(panel_a[3]), FadeIn(panel_b[3]), run_time=0.5)
    scene.play(FadeIn(both), run_time=0.5)
    scene.play(FadeIn(fair), run_time=0.4)
    scene.wait(2.2)
    if fade_out:
        scene.play(FadeOut(*scene.mobjects), run_time=0.5)


# ------------------------------------------------------------------ chapter 2: full-label reference

PANEL_WIDTH = 6.3


def _fit_panel(mobjects: list[Text], width: float = PANEL_WIDTH) -> None:
    for mob in mobjects:
        if mob.width > width:
            mob.scale_to_fit_width(width)


def chapter_reference_segment(scene: Scene, ctx: LongContext, fade_out: bool = True) -> None:
    style = ctx.style
    a, b = ctx.pair.rule_a, ctx.pair.rule_b
    ref_b = [r.map50_95 for r in b.reference.values()]
    ref_a = [r.map50_95 for r in a.reference.values()]
    y_max = round(max(ref_b) * 1.2 + 0.005, 2)
    axes = _axes(ctx.short, y_max).to_edge(LEFT, buff=0.7).shift(UP * 0.2)
    lines = VGroup(*[_line(axes, b.mean_curve[arm], style.colors[arm], 4) for arm in ARMS])
    legend = arm_legend(ctx).next_to(axes, UP, buff=0.3)
    scene.play(Create(axes), FadeIn(legend), run_time=0.6)
    scene.play(Create(lines), run_time=1.2)

    ref_line = DashedLine(
        axes.c2p(0, b.reference_mean), axes.c2p(0.22, b.reference_mean),
        color=style.colors["muted"], stroke_width=3,
    )
    head = text_long(ctx, "ch2_ref_line", "label")
    head_range = text_long(ctx, "ch2_ref_range", "small", style.colors["muted"])
    _fit_panel([head, head_range])
    panel = VGroup(head, head_range).arrange(DOWN, aligned_edge=LEFT, buff=0.15).to_edge(RIGHT, buff=0.6).shift(UP * 1.6)
    scene.play(Create(ref_line), FadeIn(panel), run_time=1.0)
    scene.wait(1.2)

    ratio = text_long(ctx, "ch2_ratio", "caption")
    _fit_panel([ratio])
    ratio.next_to(panel, DOWN, buff=0.5, aligned_edge=LEFT)
    scene.play(FadeIn(ratio), run_time=0.6)
    scene.wait(2.0)

    band = Polygon(
        axes.c2p(0, min(ref_a)), axes.c2p(0.22, min(ref_a)), axes.c2p(0.22, max(ref_a)), axes.c2p(0, max(ref_a)),
        fill_color=style.colors["muted"], fill_opacity=0.25, stroke_width=0,
    )
    ref_a_text = text_long(ctx, "ch2_ref_a", "caption", style.colors["start"])
    ref_a_note = text_long(ctx, "ch2_ref_a_note", "small", style.colors["muted"])
    VGroup(ref_a_text, ref_a_note).arrange(DOWN, buff=0.15).to_edge(DOWN, buff=0.4)
    scene.play(FadeIn(band), FadeIn(ref_a_text), run_time=0.8)
    scene.play(FadeIn(ref_a_note), run_time=0.5)
    scene.wait(2.4)
    if fade_out:
        scene.play(FadeOut(*scene.mobjects), run_time=0.5)


# ------------------------------------------------------------------ scenes


class ChapterReference(Scene):
    def construct(self) -> None:
        chapter_reference_segment(self, make_long_context(), fade_out=False)


class ChapterRules(Scene):
    def construct(self) -> None:
        chapter_rules_segment(self, make_long_context(), fade_out=False)


class ChapterRulesBars(Scene):
    """Inspection only: the bar chart after switching to rule B (not part of the smoke set)."""

    def construct(self) -> None:
        ctx = make_long_context()
        bars, ticks, counts = _bars(ctx)
        steps_b = _epoch_labels(ctx, bars, "bar_steps_b", ctx.style.colors["text"])
        epochs_b = _epoch_labels(ctx, bars, "bar_epochs_b", ctx.style.colors["start"])
        for step_label, epoch_label in zip(steps_b, epochs_b):
            epoch_label.next_to(step_label, UP, buff=0.08)
        rule_b = text_long(ctx, "ch1_rule_b", "label").to_edge(UP, buff=0.5)
        rule_b_note = text_long(ctx, "ch1_rule_b_note", "caption", ctx.style.colors["muted"]).next_to(rule_b, DOWN, buff=0.2)
        self.add(bars, ticks, counts, steps_b, epochs_b, rule_b, rule_b_note)
        self.wait(0.5)
