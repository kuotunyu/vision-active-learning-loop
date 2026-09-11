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
