from dataclasses import dataclass, replace
from enum import StrEnum


class Theme(StrEnum):
    SERENE = "serene"
    PAVILION = "pavilion"


class DayVariant(StrEnum):
    """A theme's look by day. Pavilion: teal or crimson. Serene: scroll-coloured or green."""

    TEAL = "teal"
    CRIMSON = "crimson"
    SCROLL = "scroll"
    GREEN = "green"


VARIANTS: dict[Theme, frozenset[DayVariant]] = {
    Theme.PAVILION: frozenset({DayVariant.TEAL, DayVariant.CRIMSON}),
    Theme.SERENE: frozenset({DayVariant.SCROLL, DayVariant.GREEN}),
}


class ReadingFont(StrEnum):
    """The face for text the user wrote. Atkinson Hyperlegible Next is the default."""

    ATKINSON = "atkinson"
    OPENDYSLEXIC = "opendyslexic"


class HeaderChoice(StrEnum):
    """What fills the header band. `auto` is the theme's live peak (it follows the time of day);
    `custom` is the user's own picture."""

    AUTO = "auto"
    CUSTOM = "custom"


def read_header_choice(saved: str | None) -> HeaderChoice:
    """A stored choice. The three built-in pictures were retired for the peak (owner, 2026-10-23):
    a choice of one of them, or anything unknown, reads as the peak."""
    return HeaderChoice.CUSTOM if saved == HeaderChoice.CUSTOM else HeaderChoice.AUTO


class Phase(StrEnum):
    DAY = "day"
    GOLDEN = "golden"
    DUSK = "dusk"


class AppearanceError(ValueError):
    """A choice that cannot be made. The message is shown to the user."""


@dataclass(frozen=True)
class Preferences:
    theme: Theme = Theme.SERENE
    day_variant: DayVariant = DayVariant.TEAL  # Pavilion's
    serene_variant: DayVariant = DayVariant.SCROLL
    reading_font: ReadingFont = ReadingFont.ATKINSON
    header: HeaderChoice = HeaderChoice.AUTO
    # Counts the user's uploads (0 = none yet), so a new picture is fetched afresh.
    header_version: int = 0


@dataclass(frozen=True)
class Appearance:
    theme: Theme
    day_variant: DayVariant | None
    phase: Phase
    # Serene's saved look, also while Pavilion shows: the Serene orb shows what choosing it gives.
    serene_variant: DayVariant = DayVariant.SCROLL
    reading_font: ReadingFont = ReadingFont.ATKINSON
    header: HeaderChoice = HeaderChoice.AUTO
    header_version: int = 0


def resolve_appearance(prefs: Preferences, phase: Phase = Phase.DAY) -> Appearance:
    """What the UI should look like right now: the theme with its own day variant.

    The phase comes from the sunset system (`domain/sunset.py`); at dusk each theme has one look.
    """
    variant = prefs.day_variant if prefs.theme is Theme.PAVILION else prefs.serene_variant
    return Appearance(
        theme=prefs.theme,
        day_variant=variant,
        phase=phase,
        serene_variant=prefs.serene_variant,
        reading_font=prefs.reading_font,
        header=prefs.header,
        header_version=prefs.header_version,
    )


def choose_theme(prefs: Preferences, theme: Theme, variant: DayVariant | None) -> Preferences:
    """Pick a theme, and with it one of its own day variants. Each theme keeps its variant, so
    leaving Serene's green for Pavilion and coming back finds it green again."""
    if variant is None:
        return replace(prefs, theme=theme)
    if variant not in VARIANTS[theme]:
        raise AppearanceError(f"{theme.value.title()} has no {variant.value} look")
    if theme is Theme.SERENE:
        return replace(prefs, theme=theme, serene_variant=variant)
    return replace(prefs, theme=theme, day_variant=variant)


def choose_header(prefs: Preferences, choice: HeaderChoice) -> Preferences:
    """Pick a header picture. The user's own can be picked once one has been uploaded."""
    if choice is HeaderChoice.CUSTOM and prefs.header_version == 0:
        raise AppearanceError("Choose a picture of your own first")
    return replace(prefs, header=choice)


def with_uploaded_header(prefs: Preferences) -> Preferences:
    """A new picture of the user's own is now the header."""
    return replace(prefs, header=HeaderChoice.CUSTOM, header_version=prefs.header_version + 1)
