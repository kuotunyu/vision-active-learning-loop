import pytest

from val_explainer.copy import BANNED, COPY, MAX_CHARS_PER_LINE, NEGATIONS, display_width, render_copy
from val_explainer.data import format_delta, load_explainer_data

EXPECTED_KEYS = {
    "title", "title_sub",
    "pool_label", "test_label", "start_label",
    "lane_random", "lane_entropy", "lane_margin", "score", "retrain", "evaluate", "loop_caption",
    "axis_x", "axis_y", "delta_title", "delta_seed", "sign", "range_note",
    "outro_1", "outro_2", "outro_3", "outro_path",
}


def test_copy_has_exactly_the_frozen_keys():
    assert set(COPY) == EXPECTED_KEYS


def test_every_line_is_non_empty_and_fits():
    rendered = render_copy(load_explainer_data())
    for key, text in rendered.items():
        assert text.strip(), key
        for line in text.split("\n"):
            assert display_width(line) <= MAX_CHARS_PER_LINE, (key, line, display_width(line))


def test_display_width_counts_cjk_as_one_and_ascii_as_about_half():
    assert display_width("中文") == 2.0
    assert display_width("ab") == pytest.approx(1.1)
    assert display_width("（）") == 2.0


@pytest.mark.parametrize("phrase", BANNED)
def test_banned_phrases_only_appear_negated(phrase):
    rendered = render_copy(load_explainer_data())
    for key, text in rendered.items():
        if phrase.lower() in text.lower():
            assert any(neg in text for neg in NEGATIONS), (key, text)


def test_rendered_numbers_come_from_data():
    data = load_explainer_data()
    rendered = render_copy(data)
    assert f"{data.pool_size:,}" in rendered["pool_label"]
    assert str(data.test_size) in rendered["test_label"]
    assert str(data.start_count()) in rendered["start_label"]
    for seed in data.seeds:
        line = rendered[f"delta_seed_{seed}"]
        assert str(seed) in line
        assert format_delta(data.delta["margin"][seed]) in line
    n = data.positive_seed_count("margin")
    assert f"{n}/{len(data.seeds)}" in rendered["sign"]


def test_the_three_frozen_negative_sentences_are_present():
    rendered = render_copy(load_explainer_data())
    assert rendered["range_note"] == "三個 seed 的最大最小是範圍，不是信賴區間"
    assert rendered["outro_3"] == "不宣稱降低標註成本；同機重播並非位元相同"


# ------------------------------------------------------------------ long version

from val_explainer.copy import COPY_LONG, intervals_overlap, render_copy_long  # noqa: E402
from val_explainer.data import BUDGET_KEYS, ExplainerDataError, load_rule_pair, range_text  # noqa: E402

EXPECTED_LONG_KEYS = {
    "ch1_title", "ch1_sub", "ch1_rule_a", "ch1_rule_a_epochs", "ch1_rule_b", "ch1_rule_b_note", "ch1_computed",
    "ch1_sign_a", "ch1_sign_b", "ch1_both", "ch1_fair", "ch1_axis_a", "ch1_axis_b",
    "ch2_ref_line", "ch2_ref_range", "ch2_ratio", "ch2_ref_a", "ch2_ref_a_note",
    "ch3_title", "ch3_sub", "ch3_a", "ch3_a_ranges", "ch3_b", "ch3_b_note",
    "close_1", "close_2", "close_path",
}


def test_copy_long_has_exactly_the_frozen_keys():
    assert set(COPY_LONG) == EXPECTED_LONG_KEYS


def test_long_lines_fit_and_banned_phrases_are_negated():
    rendered = render_copy_long(load_rule_pair())
    for key, text in rendered.items():
        assert text.strip(), key
        for line in text.split("\n"):
            assert display_width(line) <= MAX_CHARS_PER_LINE, (key, line, display_width(line))
        for phrase in BANNED:
            if phrase.lower() in text.lower():
                assert any(neg in text for neg in NEGATIONS), (key, text)


def test_long_numbers_come_from_data():
    pair = load_rule_pair()
    a, b = pair.rule_a, pair.rule_b
    rendered = render_copy_long(pair)
    assert f"{a.steps['0.02']:,}" in rendered["ch1_rule_a"]
    assert str(a.epochs["0.02"]) in rendered["ch1_rule_a_epochs"] and str(a.epochs["0.20"]) in rendered["ch1_rule_a_epochs"]
    assert str(b.epochs["0.20"]) in rendered["ch1_rule_b"] and str(b.steps["0.02"]) in rendered["ch1_rule_b"]
    assert range_text([r.map50_95 for r in b.reference.values()], 4) in rendered["ch2_ref_range"]
    assert range_text(b.arm_values_20("ratio_20", "random"), 2) in rendered["ch2_ratio"]
    assert str(a.reference[17].epochs) in rendered["ch2_ref_a"]
    assert range_text(a.arm_values_20("min_recall_20", "margin"), 3) in rendered["ch3_a_ranges"]
    assert range_text(b.arm_values_20("min_recall_20", "random"), 3) in rendered["ch3_b"]
    for key in BUDGET_KEYS:
        assert rendered[f"bar_images_{key}"] == f"{b.budgets[key]} 張"
        assert rendered[f"bar_epochs_a_{key}"] == f"{a.epochs[key]} epoch"
        assert rendered[f"bar_steps_b_{key}"] == f"{b.steps[key]:,} 步"
        assert rendered[f"bar_epochs_b_{key}"] == f"{b.epochs[key]} epoch"


def test_intervals_overlap():
    assert intervals_overlap([0.1, 0.3], [0.2, 0.5])
    assert not intervals_overlap([0.1, 0.2], [0.3, 0.4])
    assert intervals_overlap([0.1, 0.3], [0.3, 0.4])


def test_claims_are_verified_against_data():
    pair = load_rule_pair()
    rendered = render_copy_long(pair)
    assert rendered["close_1"] == "不宣稱降低標註成本；同機重播並非位元相同"
    assert rendered["close_2"] == "三個 seed 的最大最小是範圍，不是信賴區間"
    # forge a pair whose rule-A recall intervals overlap: the "互不重疊" sentence must refuse to render
    import dataclasses
    forged_recall = {seed: dict(row) for seed, row in pair.rule_a.min_recall_20.items()}
    first = pair.rule_a.seeds[0]
    forged_recall[first]["random"] = forged_recall[first]["margin"]
    forged_a = dataclasses.replace(pair.rule_a, min_recall_20=forged_recall)
    with pytest.raises(ExplainerDataError, match="ch3_a"):
        render_copy_long(dataclasses.replace(pair, rule_a=forged_a))
