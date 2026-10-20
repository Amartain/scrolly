from scrolly.domain.legend import Legend, Overrides, build_legend, with_symbol
from scrolly.ports import Clock, Store

KEY = "legend"


def load_overrides(store: Store) -> Overrides:
    saved = store.settings.get(KEY)
    return {} if saved is None else dict(saved)


def load_legend(store: Store) -> Legend:
    """The Legend of the Scrolls with the user's own symbols laid over the defaults."""
    return build_legend(load_overrides(store))


class LegendService:
    def __init__(self, store: Store, clock: Clock) -> None:
        self._store = store
        self._clock = clock

    def set_symbol(self, group: str, key: str, emoji: str | None, shortcode: str | None) -> None:
        """Change one symbol; give neither emoji nor shortcode to restore the default."""
        mine = with_symbol(load_overrides(self._store), group, key, emoji, shortcode)
        self._store.settings.set(KEY, dict(mine), self._clock.now())
