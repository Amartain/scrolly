from dataclasses import replace

from scrolly.domain.appearance import (
    DayVariant,
    HeaderChoice,
    Preferences,
    ReadingFont,
    Theme,
    choose_header,
    choose_theme,
    with_uploaded_header,
)
from scrolly.ports import Clock, Store

KEY = "appearance"


class AppearanceService:
    def __init__(self, store: Store, clock: Clock) -> None:
        self._store = store
        self._clock = clock

    def preferences(self) -> Preferences:
        saved = self._store.settings.get(KEY)
        if saved is None:
            return Preferences()
        return Preferences(
            theme=Theme(saved["theme"]),
            day_variant=DayVariant(saved["day_variant"]),
            serene_variant=DayVariant(saved.get("serene_variant", DayVariant.SCROLL)),
            reading_font=ReadingFont(saved.get("reading_font", ReadingFont.ATKINSON)),
            header=HeaderChoice(saved.get("header", HeaderChoice.AUTO)),
            header_version=int(saved.get("header_version", 0)),
        )

    def choose(self, theme: Theme, day_variant: DayVariant | None) -> Preferences:
        """Remember the user's pick. Without a variant, the theme's previous one is kept."""
        prefs = choose_theme(self.preferences(), theme, day_variant)
        self._save(prefs)
        return prefs

    def choose_reading_font(self, font: ReadingFont) -> Preferences:
        prefs = replace(self.preferences(), reading_font=font)
        self._save(prefs)
        return prefs

    def choose_header(self, choice: HeaderChoice) -> Preferences:
        prefs = choose_header(self.preferences(), choice)
        self._save(prefs)
        return prefs

    def use_uploaded_header(self) -> Preferences:
        """The picture file was saved: it becomes the header."""
        prefs = with_uploaded_header(self.preferences())
        self._save(prefs)
        return prefs

    def _save(self, prefs: Preferences) -> None:
        value = {
            "theme": prefs.theme.value,
            "day_variant": prefs.day_variant.value,
            "serene_variant": prefs.serene_variant.value,
            "reading_font": prefs.reading_font.value,
            "header": prefs.header.value,
            "header_version": prefs.header_version,
        }
        self._store.settings.set(KEY, value, self._clock.now())
        self._store.commit()
