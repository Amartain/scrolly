from datetime import datetime

from scrolly.domain.dispatch import DispatchOptions, render_dispatch
from scrolly.domain.logical_day import logical_day
from scrolly.ports import Clock, Store
from scrolly.services.legend import load_legend

KEY = "dispatch"


def load_options(store: Store) -> DispatchOptions:
    saved = store.settings.get(KEY) or {}
    return DispatchOptions(
        dnd=bool(saved.get("dnd", False)),
        include_postponed=bool(saved.get("include_postponed", False)),
        include_abandoned=bool(saved.get("include_abandoned", False)),
    )


def build_dispatch(store: Store, now: datetime) -> str:
    """Today's scroll as Discord markdown, in the user's symbols and with their options."""
    today = logical_day(now)
    return render_dispatch(
        today, store.trials.list_for_day(today), load_legend(store), load_options(store)
    )


class DispatchService:
    def __init__(self, store: Store, clock: Clock) -> None:
        self._store = store
        self._clock = clock

    def choose(
        self,
        dnd: bool | None = None,
        include_postponed: bool | None = None,
        include_abandoned: bool | None = None,
    ) -> DispatchOptions:
        """Only what is given changes."""
        current = load_options(self._store)
        options = DispatchOptions(
            dnd=current.dnd if dnd is None else dnd,
            include_postponed=(
                current.include_postponed if include_postponed is None else include_postponed
            ),
            include_abandoned=(
                current.include_abandoned if include_abandoned is None else include_abandoned
            ),
        )
        self._store.settings.set(
            KEY,
            {
                "dnd": options.dnd,
                "include_postponed": options.include_postponed,
                "include_abandoned": options.include_abandoned,
            },
            self._clock.now(),
        )
        return options
