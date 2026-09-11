"""Font, colours and sizes. Okabe-Ito colours; a CJK font is mandatory."""

from __future__ import annotations

from dataclasses import dataclass, field

FONT_CANDIDATES = ("Microsoft JhengHei", "Noto Sans TC")


def resolve_font(available: list[str] | None = None) -> str:
    if available is None:
        import manimpango

        available = list(manimpango.list_fonts())
    for candidate in FONT_CANDIDATES:
        if candidate in available:
            return candidate
    raise RuntimeError(f"no CJK font installed; expected one of {FONT_CANDIDATES}")


@dataclass(frozen=True)
class Style:
    font: str
    colors: dict[str, str] = field(
        default_factory=lambda: {
            "random": "#999999",
            "entropy": "#0072B2",
            "margin": "#E69F00",
            "start": "#F0E442",
            "pool": "#3A3A3A",
            "test": "#2B4C6F",
            "text": "#FFFFFF",
            "muted": "#BBBBBB",
        }
    )
    sizes: dict[str, int] = field(
        default_factory=lambda: {
            "title": 48,
            "sub": 28,
            "label": 26,
            "caption": 24,
            "small": 20,
            "counter": 32,
        }
    )
    cell: float = 0.085
    cell_gap: float = 0.025


def default_style() -> Style:
    return Style(font=resolve_font())
