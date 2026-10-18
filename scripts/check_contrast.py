"""Keep text, gauges and surfaces in range in every theme, reading the token files directly.

- Text tokens need 4.5:1 (WCAG AA) on the panel and raised surfaces they are drawn on.
- Gauge fills need 3:1 against the gauge track (`--inset`), since the track is bordered and
  labelled.
- Cards: each card's ink (and the Mandate on the Horizon) needs 4.5:1 on its head and row overlays
  laid over both gradient stops.
- Serene themes: no surface is brighter than `--surface-canvas`. Highlights (inset top line,
  button sheen, icon highlight shapes) are not surfaces and are not checked. Dusk is dark, so its
  coloured accent fills (cards, action and entry buttons) are exempt; only neutral surfaces count.
"""

import re
import sys
from pathlib import Path

TOKENS = Path(__file__).resolve().parent.parent / "frontend" / "src" / "styles" / "tokens"
SURFACES = ("--surface-panel", "--surface-raised")
TEXT = ("--ink", "--ink-muted", "--mandate", "--growth-text")
GAUGE = ("--qi-calm", "--qi-surge", "--qi-redline")
DECLARATION = re.compile(r"(--[\w-]+)\s*:\s*(#[0-9a-fA-F]{6})\s*;")
OVERLAY = re.compile(r"(--[\w-]+)\s*:\s*rgba\((\d+),\s*(\d+),\s*(\d+),\s*([\d.]+)\)\s*;")
FIRST_RGBA = re.compile(r"rgba\((\d+),\s*(\d+),\s*(\d+),\s*([\d.]+)\)")

# Neutral surfaces (checked in every Serene theme), then colour fills (Serene Day only).
NEUTRAL_SURFACES = (
    "--surface-panel",
    "--surface-stripe",
    "--surface-raised",
    "--inset",
    "--btn",
    "--head-bg",
    "--strong",
)
COLOR_SURFACES = (
    "--promote-bg",
    "--card-horizon-a",
    "--card-horizon-b",
    "--card-foundational-a",
    "--card-foundational-b",
    "--card-restorative-a",
    "--card-restorative-b",
    "--card-horizon-action-bg",
    "--card-foundational-action-bg",
    "--card-restorative-action-bg",
    "--entry-archives-bg",
    "--entry-dispatch-bg",
    "--entry-settings-bg",
)
KINDS = ("horizon", "foundational", "restorative")
BANDS = ("head", "row-a", "row-b")

Color = tuple[float, float, float]


def rgb(color: str) -> Color:
    return (int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16))


def over(top: Color, alpha: float, base: Color) -> Color:
    return (
        top[0] * alpha + base[0] * (1 - alpha),
        top[1] * alpha + base[1] * (1 - alpha),
        top[2] * alpha + base[2] * (1 - alpha),
    )


def luminance(color: str | Color) -> float:
    channels = [c / 255 for c in (rgb(color) if isinstance(color, str) else color)]
    linear = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def ratio(first: str, second: str) -> float:
    high, low = sorted((luminance(first), luminance(second)), reverse=True)
    return (high + 0.05) / (low + 0.05)


def contrast_problems(name: str, values: dict[str, str]) -> list[str]:
    found = []
    pairs = [(t, s, 4.5) for t in TEXT for s in SURFACES] + [(g, "--inset", 3.0) for g in GAUGE]
    for token, surface, needed in pairs:
        if token not in values or surface not in values:
            found.append(f"{name}: {token} or {surface} is missing")
            continue
        got = ratio(values[token], values[surface])
        if got < needed:
            found.append(f"{name}: {token} on {surface} is {got:.2f}:1, needs {needed}:1")
    return found


def brightness_problems(name: str, text: str, values: dict[str, str]) -> list[str]:
    limit = luminance(values["--surface-canvas"])
    day = "dusk" not in name
    tokens = NEUTRAL_SURFACES + (COLOR_SURFACES if day else ())
    fills = {token: rgb(values[token]) for token in tokens if token in values}
    if not day:
        return _too_bright(name, fills, limit)
    for token, band in card_bands(text, values):
        fills[token] = band
    sheen = FIRST_RGBA.search(_declaration(text, "--gloss-faint"))
    if sheen and "--surface-panel" in values:
        white = (float(sheen[1]), float(sheen[2]), float(sheen[3]))
        fills["--gloss-faint on --surface-panel"] = over(
            white, float(sheen[4]), rgb(values["--surface-panel"])
        )
    return _too_bright(name, fills, limit)


def _too_bright(name: str, fills: dict[str, Color], limit: float) -> list[str]:
    return [
        f"{name}: {token} is brighter than --surface-canvas"
        for token, color in fills.items()
        if luminance(color) > limit + 1e-9
    ]


def card_bands(text: str, values: dict[str, str]) -> list[tuple[str, Color]]:
    """Every card band (head, rows) as the solid colour it shows on each gradient stop."""
    bands = []
    for token, red, green, blue, alpha in _overlays(text):
        kind = token.split("-")[3] if token.startswith("--card-") else ""
        for stop in "ab":
            fill = values.get(f"--card-{kind}-{stop}")
            if fill and token.removeprefix(f"--card-{kind}-") in BANDS:
                color = over((float(red), float(green), float(blue)), alpha, rgb(fill))
                bands.append((f"{token} on --card-{kind}-{stop}", color))
    return bands


def card_problems(name: str, text: str, values: dict[str, str]) -> list[str]:
    found = []
    for token, band in card_bands(text, values):
        kind = token.split("-")[3]
        inks = [f"--card-{kind}-ink"] + (["--card-horizon-mandate"] if kind == "horizon" else [])
        for ink in inks:
            if ink not in values:
                found.append(f"{name}: {ink} is missing")
                continue
            high, low = sorted((luminance(values[ink]), luminance(band)), reverse=True)
            got = (high + 0.05) / (low + 0.05)
            if got < 4.5:
                found.append(f"{name}: {ink} on {token} is {got:.2f}:1, needs 4.5:1")
    return found


def _overlays(text: str) -> list[tuple[str, int, int, int, float]]:
    return [(t, int(r), int(g), int(b), float(a)) for t, r, g, b, a in OVERLAY.findall(text)]


def _declaration(text: str, token: str) -> str:
    match = re.search(re.escape(token) + r"\s*:\s*([^;]+);", text)
    return match[1] if match else ""


def problems(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    values = dict(DECLARATION.findall(text))
    found = contrast_problems(path.name, values) + card_problems(path.name, text, values)
    if path.name.startswith("serene") and "--surface-canvas" in values:
        found += brightness_problems(path.name, text, values)
    return found


def main() -> int:
    files = sorted(TOKENS.glob("*.css"))
    themes = [path for path in files if path.name != "base.css"]
    found = [issue for path in themes for issue in problems(path)]
    print("\n".join(found) or f"Contrast check passed ({len(themes)} themes).")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
