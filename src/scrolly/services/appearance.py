from scrolly.domain.appearance import DayVariant, Preferences, Theme
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
        )

    def choose(self, theme: Theme, day_variant: DayVariant | None) -> Preferences:
        """Remember the user's pick. Without a variant, the previous one is kept."""
        variant = day_variant or self.preferences().day_variant
        prefs = Preferences(theme=theme, day_variant=variant)
        value = {"theme": prefs.theme.value, "day_variant": prefs.day_variant.value}
        self._store.settings.set(KEY, value, self._clock.now())
        self._store.commit()
        return prefs
