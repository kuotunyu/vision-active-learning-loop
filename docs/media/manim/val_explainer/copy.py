"""On-screen wording, frozen by the design spec (Section 1). Change the spec before changing this."""

from __future__ import annotations

import unicodedata

from .data import ExplainerData, format_delta

# Display width in CJK character units: wide/fullwidth glyphs count 1, everything else 0.55.
MAX_CHARS_PER_LINE = 34
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
