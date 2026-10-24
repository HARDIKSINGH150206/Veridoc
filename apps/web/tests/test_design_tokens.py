"""Tests for apps/web/assets/design-tokens.css and fonts.css (written before the files)."""

import re
from pathlib import Path

import pytest

ASSETS = Path(__file__).resolve().parent.parent / "assets"
TOKENS = (ASSETS / "design-tokens.css").read_text(encoding="utf-8")
FONTS_CSS = (ASSETS / "fonts.css").read_text(encoding="utf-8")

STATUSES = ["clear", "ambiguous", "missing", "conflict"]
SYMBOLS = {"clear": "✓", "ambiguous": "!", "missing": "○", "conflict": "⚠"}
LABELS = {"clear": "Clear", "ambiguous": "Ambiguous", "missing": "Missing", "conflict": "Conflict"}


def parse_vars(block: str) -> dict[str, str]:
    return {
        name: value.strip() for name, value in re.findall(r"(--[a-z0-9-]+)\s*:\s*([^;]+);", block)
    }


def blocks() -> tuple[dict[str, str], dict[str, str], dict[str, str]]:
    light = re.search(r"(?m)^:root\s*\{(.*?)^\}", TOKENS, re.S)
    media = re.search(
        r"@media \(prefers-color-scheme: dark\)\s*\{\s*"
        r':root:not\(\[data-theme="light"\]\)\s*\{(.*?)\}\s*\}',
        TOKENS,
        re.S,
    )
    forced = re.search(r'(?m)^:root\[data-theme="dark"\]\s*\{(.*?)^\}', TOKENS, re.S)
    assert light and media and forced, "light, media-dark and forced-dark blocks must exist"
    return parse_vars(light.group(1)), parse_vars(media.group(1)), parse_vars(forced.group(1))


LIGHT, DARK_MEDIA, DARK_FORCED = blocks()


def luminance(hex_colour: str) -> float:
    h = hex_colour.lstrip("#")
    r, g, b = (int(h[i : i + 2], 16) / 255 for i in (0, 2, 4))

    def lin(c: float) -> float:
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def contrast(a: str, b: str) -> float:
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def theme(name: str) -> dict[str, str]:
    return LIGHT if name == "light" else {**LIGHT, **DARK_FORCED}


def test_dark_theme_is_defined_twice_identically() -> None:
    """Once for the system preference, once for the manual switch (data-theme=dark)."""
    assert {k: v for k, v in DARK_FORCED.items()} == DARK_MEDIA


def test_dark_theme_overrides_exactly_the_colour_tokens() -> None:
    overridden = {k for k in DARK_FORCED if k != "color-scheme"}
    light_colours = {k for k, v in LIGHT.items() if re.fullmatch(r"#[0-9A-Fa-f]{6}", v)}
    assert overridden == light_colours


@pytest.mark.parametrize("status", STATUSES)
def test_every_status_has_colours_symbol_and_word(status: str) -> None:
    for part in ("fg", "bg", "border"):
        assert f"--status-{status}-{part}" in LIGHT
    assert LIGHT[f"--status-{status}-symbol"] == f'"{SYMBOLS[status]}"'
    assert LIGHT[f"--status-{status}-label"] == f'"{LABELS[status]}"'


def test_status_symbols_are_all_different() -> None:
    assert len(set(SYMBOLS.values())) == 4


@pytest.mark.parametrize("mode", ["light", "dark"])
@pytest.mark.parametrize("fg,bg", [
    ("--color-text", "--color-bg"),
    ("--color-text", "--color-surface"),
    ("--color-text", "--color-surface-alt"),
    ("--color-text-muted", "--color-bg"),
    ("--color-text-muted", "--color-surface"),
    ("--color-on-accent", "--color-accent"),
    ("--color-accent", "--color-surface"),
    ("--color-accent", "--color-bg"),
    ("--status-clear-fg", "--status-clear-bg"),
    ("--status-ambiguous-fg", "--status-ambiguous-bg"),
    ("--status-missing-fg", "--status-missing-bg"),
    ("--status-conflict-fg", "--status-conflict-bg"),
])  # fmt: skip
def test_text_colours_meet_wcag_aa(mode: str, fg: str, bg: str) -> None:
    t = theme(mode)
    assert contrast(t[fg], t[bg]) >= 4.5, f"{mode}: {fg} on {bg}"


@pytest.mark.parametrize("mode", ["light", "dark"])
def test_borders_and_focus_are_visible(mode: str) -> None:
    t = theme(mode)
    assert contrast(t["--color-focus"], t["--color-surface"]) >= 3
    assert contrast(t["--color-border"], t["--color-surface"]) >= 1.4


def test_type_scale_base_is_at_least_16_px_and_scales_with_the_user() -> None:
    assert LIGHT["--font-size-base"] == "1rem"
    sizes = [
        LIGHT[f"--font-size-{s}"] for s in ("xs", "sm", "base", "md", "lg", "xl", "2xl", "3xl")
    ]
    assert all(s.endswith("rem") for s in sizes), "sizes must be rem so 200% zoom works"
    values = [float(s[:-3]) for s in sizes]
    assert values == sorted(values) and len(set(values)) == len(values)


def test_spacing_scale_is_rem_on_a_quarter_rem_grid() -> None:
    spaces = {k: v for k, v in LIGHT.items() if k.startswith("--space-")}
    assert len(spaces) >= 6
    for name, value in spaces.items():
        assert value.endswith("rem"), name
        assert (float(value[:-3]) * 4) % 1 == 0, f"{name} is off the 0.25rem grid"


def test_radii_and_layout_tokens_exist() -> None:
    for name in ("--radius-sm", "--radius-md", "--radius-lg", "--radius-pill", "--radius-round"):
        assert name in LIGHT
    assert LIGHT["--layout-max"] == "70rem"  # 1120 px desktop layout from the wireframes


def test_font_stack_names_the_bundled_scripts_first() -> None:
    stack = LIGHT["--font-body"]
    for family in ("Noto Sans", "Noto Sans Devanagari", "Noto Sans Kannada"):
        assert f'"{family}"' in stack
    assert "sans-serif" in stack
    assert "--line-height-indic" in LIGHT


def test_reduced_motion_turns_durations_off() -> None:
    assert re.search(r"prefers-reduced-motion:\s*reduce", TOKENS)


# ---- fonts are bundled, offline and licensed ----


def test_font_faces_point_at_files_that_exist() -> None:
    urls = re.findall(r"url\(['\"]?([^'\")]+)['\"]?\)", FONTS_CSS)
    assert len(urls) == 6, "regular and bold for Latin, Devanagari and Kannada"
    for url in urls:
        assert not url.startswith(("http:", "https:", "//", "data:")), url
        assert (ASSETS / url).is_file(), url


def test_every_font_file_is_used_and_has_a_licence() -> None:
    used = {Path(u).name for u in re.findall(r"url\(['\"]?([^'\")]+)['\"]?\)", FONTS_CSS)}
    shipped = {p.name for p in (ASSETS / "fonts").glob("*.woff2")}
    assert used == shipped
    licence = (ASSETS / "fonts" / "OFL-NotoSans.txt").read_text(encoding="utf-8")
    assert "SIL Open Font License" in licence


def test_font_faces_cover_rupee_and_indic_ranges() -> None:
    assert "U+0900-097F" in FONTS_CSS  # Devanagari
    assert "U+0C80-0CF3" in FONTS_CSS  # Kannada
    assert "U+20B9" in FONTS_CSS  # rupee sign
    assert FONTS_CSS.count("font-display: swap") == 6
