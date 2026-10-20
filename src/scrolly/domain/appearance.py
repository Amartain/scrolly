from dataclasses import dataclass
from enum import StrEnum


class Theme(StrEnum):
    SERENE = "serene"
    PAVILION = "pavilion"


class DayVariant(StrEnum):
    TEAL = "teal"
    CRIMSON = "crimson"


class ReadingFont(StrEnum):
    """The face for text the user wrote. Atkinson Hyperlegible Next is the default."""

    ATKINSON = "atkinson"
    OPENDYSLEXIC = "opendyslexic"


class Phase(StrEnum):
    DAY = "day"
    GOLDEN = "golden"
    DUSK = "dusk"


@dataclass(frozen=True)
class Preferences:
    theme: Theme = Theme.SERENE
    day_variant: DayVariant = DayVariant.TEAL
    reading_font: ReadingFont = ReadingFont.ATKINSON


@dataclass(frozen=True)
class Appearance:
    theme: Theme
    day_variant: DayVariant | None
    phase: Phase
    reading_font: ReadingFont = ReadingFont.ATKINSON


def resolve_appearance(prefs: Preferences, phase: Phase = Phase.DAY) -> Appearance:
    """What the UI should look like right now. Only Pavilion has a day variant.

    The phase comes from the sunset system (`domain/sunset.py`).
    """
    variant = prefs.day_variant if prefs.theme is Theme.PAVILION else None
    return Appearance(
        theme=prefs.theme,
        day_variant=variant,
        phase=phase,
        reading_font=prefs.reading_font,
    )
