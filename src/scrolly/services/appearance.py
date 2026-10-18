from dataclasses import replace

from scrolly.domain.appearance import DayVariant, Preferences, ReadingFont, Theme
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
            reading_font=ReadingFont(saved.get("reading_font", ReadingFont.ATKINSON)),
        )

    def choose(self, theme: Theme, day_variant: DayVariant | None) -> Preferences:
        """Remember the user's pick. Without a variant, the previous one is kept."""
        current = self.preferences()
        prefs = Preferences(
            theme=theme,
            day_variant=day_variant or current.day_variant,
            reading_font=current.reading_font,
        )
        self._save(prefs)
        return prefs

    def choose_reading_font(self, font: ReadingFont) -> Preferences:
        prefs = replace(self.preferences(), reading_font=font)
        self._save(prefs)
        return prefs

    def _save(self, prefs: Preferences) -> None:
        value = {
            "theme": prefs.theme.value,
            "day_variant": prefs.day_variant.value,
            "reading_font": prefs.reading_font.value,
        }
        self._store.settings.set(KEY, value, self._clock.now())
        self._store.commit()
