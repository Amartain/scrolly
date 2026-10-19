"""The Legend of the Scrolls: which symbol stands for which state and type.

One source for the app's icons now and the Discord Dispatch later. Emoji are the interim icons
(custom drawings come in build step 11); the handscroll in the header is the app mark, not a symbol.
"""

from dataclasses import dataclass
from enum import StrEnum

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
