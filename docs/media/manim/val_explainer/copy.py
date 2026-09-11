"""On-screen wording, frozen by the design spec (Section 1). Change the spec before changing this."""

from __future__ import annotations

import unicodedata

from .data import ARMS, BUDGET_KEYS, ExplainerData, ExplainerDataError, RulePair, format_delta, range_text

# Display width in CJK character units: wide/fullwidth glyphs count 1, everything else 0.55.
MAX_CHARS_PER_LINE = 36
NEGATIONS = ("不宣稱", "不是", "並非")
BANNED = ("降低標註成本", "信賴區間", "deterministic", "可重現")


def display_width(text: str) -> float:
    """Approximate rendered width of one line, in CJK character units."""
    return sum(1.0 if unicodedata.east_asian_width(ch) in ("W", "F") else 0.55 for ch in text)

COPY: dict[str, str] = {
    "title": "主動學習迴圈｜RDD2022 Czech × RT-DETR r18",
    "title_sub": "v0.2.1・固定 epoch 規則・{n_seeds} 個 seed",
    "pool_label": "未標註 pool {pool} 張",
    "test_label": "test {test} 張：凍結，不參與選樣與訓練",
    "start_label": "共享起點 2%＝{start} 張",
    "lane_random": "random",
    "lane_entropy": "entropy",
    "lane_margin": "margin",
    "score": "打分",
    "retrain": "重訓",
    "evaluate": "評估 mAP50-95",
    "loop_caption": "同一起點、同一 recipe、同一 test；只有選圖規則不同",
    "axis_x": "預算（pool 的比例）",
    "axis_y": "mAP50-95（test）",
    "delta_title": "配對差（margin − random）",
    "delta_seed": "seed {seed}：nAUBC {delta}",
    "sign": "{n} 個 seed 都為正（{n}/{total}）",
    "range_note": "三個 seed 的最大最小是範圍，不是信賴區間",
    "outro_1": "固定步數與固定 epoch 兩種規則下都是 3/3（entropy 亦同）",
    "outro_2": "20% 預算約達全標籤參考基線的一半",
    "outro_3": "不宣稱降低標註成本；同機重播並非位元相同",
    "outro_path": "docs/results/2026-09-11-v0.2.1-training-rule.md",
}


def render_copy(data: ExplainerData) -> dict[str, str]:
    """Fill the templates with evidence-bound numbers; one `delta_seed_<seed>` line per seed."""
    total = len(data.seeds)
    filled = {
        key: text.format(
            n_seeds=total,
            pool=f"{data.pool_size:,}",
            test=data.test_size,
            start=data.start_count(),
            n=data.positive_seed_count("margin"),
            total=total,
            seed="{seed}",
            delta="{delta}",
        )
        for key, text in COPY.items()
    }
    for seed in data.seeds:
        filled[f"delta_seed_{seed}"] = COPY["delta_seed"].format(
            seed=seed, delta=format_delta(data.delta["margin"][seed])
        )
    del filled["delta_seed"]
    return filled


# ------------------------------------------------------------------ long version

COPY_LONG: dict[str, str] = {
    "ch1_title": "為什麼要跑第二輪",
    "ch1_sub": "固定步數把預算和訓練長度綁在一起",
    "ch1_rule_a": "規則 A：每個 fit 固定 {steps_a} 步",
    "ch1_rule_a_epochs": "{start} 張跑 {epochs_a_02} 個 epoch，{n20} 張只跑 {epochs_a_20} 個",
    "ch1_rule_b": "規則 B：固定 {epochs_b} 個 epoch，最低 {min_steps} 步",
    "ch1_rule_b_note": "步數隨張數放大；2% 被最低步數托住",
    "ch1_computed": "規則 A 的 epoch 依規則算出",
    "ch1_sign_a": "Δ entropy {n_e_a}/{total}・Δ margin {n_m_a}/{total}",
    "ch1_sign_b": "Δ entropy {n_e_b}/{total}・Δ margin {n_m_b}/{total}",
    "ch1_both": "兩種規則下，entropy 與 margin 對 random 的配對差都是 {total} 個 seed 為正",
    "ch1_fair": "兩種規則回答不同的問題，不預設哪一個公平",
    "ch1_axis_a": "規則 A（固定步數）",
    "ch1_axis_b": "規則 B（固定 epoch）",
    "ch2_ref_line": "全標籤參考基線：{pool} 張全部標註、{epochs_ref_b} 個 epoch",
    "ch2_ref_range": "三個 seed 範圍 {ref_b_range}",
    "ch2_ratio": "20% 預算佔參考基線：\nrandom {ratio_random}、entropy {ratio_entropy}、margin {ratio_margin}",
    "ch2_ref_a": "規則 A 的參考基線只有 {steps_a} 步（{epochs_ref_a} 個 epoch），是欠訓的",
    "ch2_ref_a_note": "固定 GPU 成本下，全部標籤沒有比 20% 多換到 mAP；\n這不能拿來說 20% 已經足夠",
    "ch3_title": "一個負面結果",
    "ch3_sub": "20% 預算的最低類別 recall",
    "ch3_a": "v0.2-lite（規則 A）：三個 arm 的範圍互不重疊",
    "ch3_a_ranges": "random {rec_a_random}、entropy {rec_a_entropy}、margin {rec_a_margin}",
    "ch3_b": "規則 B：random {rec_b_random} 與 entropy、margin 重疊",
    "ch3_b_note": "這條證據跟訓練長度規則有關，不再單獨當作結論",
    "close_1": "不宣稱降低標註成本；同機重播並非位元相同",
    "close_2": "三個 seed 的最大最小是範圍，不是信賴區間",
    "close_path": "docs/results/2026-09-11-v0.2.1-training-rule.md",
}


def intervals_overlap(a: list[float], b: list[float]) -> bool:
    return max(min(a), min(b)) <= min(max(a), max(b))


def render_copy_long(pair: RulePair) -> dict[str, str]:
    """Fill COPY_LONG from both rules and refuse to render sentences whose claim the data no longer supports."""
    a, b = pair.rule_a, pair.rule_b
    total = len(b.seeds)
    first_seed = b.seeds[0]
    values = {
        "steps_a": f"{a.steps['0.02']:,}",
        "start": b.start_count(),
        "epochs_a_02": a.epochs["0.02"],
        "n20": b.budgets["0.20"],
        "epochs_a_20": a.epochs["0.20"],
        "epochs_b": b.epochs["0.20"],
        "min_steps": b.steps["0.02"],
        "n_e_a": a.positive_seed_count("entropy"),
        "n_m_a": a.positive_seed_count("margin"),
        "n_e_b": b.positive_seed_count("entropy"),
        "n_m_b": b.positive_seed_count("margin"),
        "total": total,
        "pool": f"{b.pool_size:,}",
        "epochs_ref_b": b.reference[first_seed].epochs,
        "ref_b_range": range_text([r.map50_95 for r in b.reference.values()], 4),
        "ratio_random": range_text(b.arm_values_20("ratio_20", "random"), 2),
        "ratio_entropy": range_text(b.arm_values_20("ratio_20", "entropy"), 2),
        "ratio_margin": range_text(b.arm_values_20("ratio_20", "margin"), 2),
        "epochs_ref_a": a.reference[first_seed].epochs,
        "rec_a_random": range_text(a.arm_values_20("min_recall_20", "random"), 3),
        "rec_a_entropy": range_text(a.arm_values_20("min_recall_20", "entropy"), 3),
        "rec_a_margin": range_text(a.arm_values_20("min_recall_20", "margin"), 3),
        "rec_b_random": range_text(b.arm_values_20("min_recall_20", "random"), 3),
    }
    # claims the sentences make
    if not all(values[k] == total for k in ("n_e_a", "n_m_a", "n_e_b", "n_m_b")):
        raise ExplainerDataError("ch1_both: not every paired delta is positive under both rules")
    rec_a = {arm: a.arm_values_20("min_recall_20", arm) for arm in ARMS}
    if (
        intervals_overlap(rec_a["random"], rec_a["entropy"])
        or intervals_overlap(rec_a["entropy"], rec_a["margin"])
        or intervals_overlap(rec_a["random"], rec_a["margin"])
    ):
        raise ExplainerDataError("ch3_a: rule-A recall ranges overlap; the sentence would be false")
    rec_b = {arm: b.arm_values_20("min_recall_20", arm) for arm in ARMS}
    if not (intervals_overlap(rec_b["random"], rec_b["entropy"]) and intervals_overlap(rec_b["random"], rec_b["margin"])):
        raise ExplainerDataError("ch3_b: rule-B random range does not overlap both arms; the sentence would be false")
    if a.reference[first_seed].epochs >= b.reference[first_seed].epochs:
        raise ExplainerDataError("ch2_ref_a: rule-A reference is not the under-trained one")
    filled = {key: text.format(**values) for key, text in COPY_LONG.items()}
    for key in BUDGET_KEYS:
        filled[f"bar_images_{key}"] = f"{b.budgets[key]} 張"
        filled[f"bar_epochs_a_{key}"] = f"{a.epochs[key]} epoch"
        filled[f"bar_steps_b_{key}"] = f"{b.steps[key]:,} 步"
        filled[f"bar_epochs_b_{key}"] = f"{b.epochs[key]} epoch"
    return filled
