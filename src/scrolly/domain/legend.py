"""The Legend of the Scrolls: which symbol stands for which state and type.

One source for the app's icons now and the Discord Dispatch later. Emoji are the interim icons
(custom drawings come in build step 11); the handscroll in the header is the app mark, not a symbol.
"""

import re
from dataclasses import dataclass, replace
from enum import StrEnum
from typing import Any

from scrolly.domain.models import ArtKind, TrialState


class TrialType(StrEnum):
    MANDATE = "mandate"
    MORTAL = "mortal"
    FOUNDATIONAL = "foundational"
    RESTORATIVE = "restorative"


@dataclass(frozen=True)
class Symbol:
    emoji: str
    shortcode: str
    label: str


STATE_SYMBOLS: dict[TrialState, Symbol] = {
    TrialState.DONE: Symbol("🍃", ":leaves:", "Conquered"),
    TrialState.IMMEDIATE: Symbol("💧", ":droplet:", "Next in flow"),
    TrialState.REMAINING: Symbol("☁️", ":cloud:", "Remaining"),
    TrialState.POSTPONED: Symbol("💤", ":zzz:", "Postponed"),
    TrialState.LOST: Symbol("🍂", ":fallen_leaf:", "Fallen leaf"),
}

TYPE_SYMBOLS: dict[TrialType, Symbol] = {
    TrialType.MANDATE: Symbol("🪷", ":lotus:", "Heavenly Mandate"),
    TrialType.MORTAL: Symbol("⚪", ":white_circle:", "Mortal Trial"),
    TrialType.FOUNDATIONAL: Symbol("📜", ":scroll:", "Foundational Art"),
    TrialType.RESTORATIVE: Symbol("🌿", ":herb:", "Restorative Art"),
}


def type_of(is_mandate: bool, art_kind: ArtKind | None) -> TrialType:
    """An instance of an Art takes the Art's type; else Mandate or Mortal."""
    if art_kind is ArtKind.FOUNDATIONAL:
        return TrialType.FOUNDATIONAL
    if art_kind is ArtKind.RESTORATIVE:
        return TrialType.RESTORATIVE
    return TrialType.MANDATE if is_mandate else TrialType.MORTAL


class LegendError(ValueError):
    """A symbol or shortcode that cannot be used. The message is shown to the user."""


@dataclass(frozen=True)
class Legend:
    """The symbols in use: the defaults above, with the user's own choices laid over them."""

    states: dict[TrialState, Symbol]
    types: dict[TrialType, Symbol]

    def symbols(self) -> list[Symbol]:
        return [*self.states.values(), *self.types.values()]


DEFAULT_LEGEND = Legend(STATE_SYMBOLS, TYPE_SYMBOLS)

# {"states": {"done": {"emoji": "🌱", "shortcode": ":seedling:"}}, "types": {...}}
Overrides = dict[str, dict[str, dict[str, str]]]

_SHORTCODE = re.compile(r":?([A-Za-z0-9_+-]{1,32}):?")
MAX_EMOJI_LENGTH = 12


def parse_shortcode(text: str) -> str:
    """`:seedling:` or `seedling`, kept as `:seedling:`."""
    match = _SHORTCODE.fullmatch(text.strip())
    if match is None:
        raise LegendError("A shortcode looks like :seedling:")
    return f":{match[1]}:"


def parse_emoji(text: str) -> str:
    cleaned = text.strip()
    if not cleaned or len(cleaned) > MAX_EMOJI_LENGTH or any(c.isspace() for c in cleaned):
        raise LegendError("A symbol is a single emoji, such as 🌱")
    return cleaned


def build_legend(overrides: Overrides) -> Legend:
    def lay(base: dict[Any, Symbol], mine: dict[str, dict[str, str]]) -> dict[Any, Symbol]:
        return {key: replace(sym, **mine.get(key.value, {})) for key, sym in base.items()}

    return Legend(
        states=lay(STATE_SYMBOLS, overrides.get("states", {})),
        types=lay(TYPE_SYMBOLS, overrides.get("types", {})),
    )


def with_symbol(
    overrides: Overrides, group: str, key: str, emoji: str | None, shortcode: str | None
) -> Overrides:
    """The overrides after changing one symbol. Giving neither emoji nor shortcode restores it.

    No two symbols may share an emoji or a shortcode, so a Dispatch can be read back.
    """
    known = {"states": {s.value for s in STATE_SYMBOLS}, "types": {t.value for t in TrialType}}
    if group not in known or key not in known[group]:
        raise LegendError("That symbol is not part of the Legend")
    mine = {g: {k: dict(v) for k, v in items.items()} for g, items in overrides.items()}
    chosen: dict[str, str] = {}
    if emoji is not None:
        chosen["emoji"] = parse_emoji(emoji)
    if shortcode is not None:
        chosen["shortcode"] = parse_shortcode(shortcode)
    if chosen:
        mine.setdefault(group, {})[key] = chosen
    else:
        mine.get(group, {}).pop(key, None)
    _require_distinct(build_legend(mine))
    return mine


def _require_distinct(legend: Legend) -> None:
    seen: dict[str, str] = {}
    for symbol in legend.symbols():
        for token in (symbol.emoji, symbol.shortcode.casefold()):
            if token in seen:
                raise LegendError(f"{token} already stands for {seen[token]}")
            seen[token] = symbol.label
