from dataclasses import dataclass, replace
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


class PanelStyle(StrEnum):
    """How every panel's header band is drawn. Paint only: both keep the same height and places."""

    PLAQUE = "plaque"  # the band, with the title on a lacquer plaque between cloud curls
    ROD = "rod"  # the band as a scroll's wooden rod with gold end caps


class HeaderChoice(StrEnum):
    """Which picture fills the header band. `auto` follows the theme and the time of day."""

    AUTO = "auto"
    SERENE_DAY = "serene-day"
    SERENE_DUSK = "serene-dusk"
    PAVILION = "pavilion"
    CUSTOM = "custom"


class Phase(StrEnum):
    DAY = "day"
    GOLDEN = "golden"
    DUSK = "dusk"


class AppearanceError(ValueError):
    """A choice that cannot be made. The message is shown to the user."""


@dataclass(frozen=True)
class Preferences:
    theme: Theme = Theme.SERENE
    day_variant: DayVariant = DayVariant.TEAL
    reading_font: ReadingFont = ReadingFont.ATKINSON
    panel_style: PanelStyle = PanelStyle.PLAQUE
    header: HeaderChoice = HeaderChoice.AUTO
    # Counts the user's uploads (0 = none yet), so a new picture is fetched afresh.
    header_version: int = 0


@dataclass(frozen=True)
class Appearance:
    theme: Theme
    day_variant: DayVariant | None
    phase: Phase
    reading_font: ReadingFont = ReadingFont.ATKINSON
    panel_style: PanelStyle = PanelStyle.PLAQUE
    header: HeaderChoice = HeaderChoice.AUTO
    header_version: int = 0


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
        panel_style=prefs.panel_style,
        header=prefs.header,
        header_version=prefs.header_version,
    )


def choose_header(prefs: Preferences, choice: HeaderChoice) -> Preferences:
    """Pick a header picture. The user's own can be picked once one has been uploaded."""
    if choice is HeaderChoice.CUSTOM and prefs.header_version == 0:
        raise AppearanceError("Choose a picture of your own first")
    return replace(prefs, header=choice)


def with_uploaded_header(prefs: Preferences) -> Preferences:
    """A new picture of the user's own is now the header."""
    return replace(prefs, header=HeaderChoice.CUSTOM, header_version=prefs.header_version + 1)
