import pytest

from val_explainer.style import FONT_CANDIDATES, Style, default_style, resolve_font


def test_prefers_jhenghei_then_noto():
    assert resolve_font(["Arial", "Noto Sans TC", "Microsoft JhengHei"]) == "Microsoft JhengHei"
    assert resolve_font(["Arial", "Noto Sans TC"]) == "Noto Sans TC"


def test_raises_when_no_cjk_font():
    with pytest.raises(RuntimeError, match="Microsoft JhengHei"):
        resolve_font(["Arial"])


def test_default_style_uses_an_installed_candidate_and_okabe_ito():
    style = default_style()
    assert isinstance(style, Style)
    assert style.font in FONT_CANDIDATES
    assert style.colors["random"] == "#999999"
    assert style.colors["entropy"] == "#0072B2"
    assert style.colors["margin"] == "#E69F00"
    assert style.cell > 0 and style.cell_gap >= 0
    for key in ("title", "sub", "label", "caption", "small", "counter"):
        assert style.sizes[key] > 0
