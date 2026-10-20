from dataclasses import replace
from datetime import datetime

from scrolly.domain.appearance import Phase
from scrolly.domain.logical_day import logical_day
from scrolly.domain.models import Day
from scrolly.domain.poems import PoemPick, poem_for
from scrolly.ports import Clock, Store
from scrolly.services.poem_content import load_poems


def build_poem(store: Store, now: datetime, phase: Phase) -> PoemPick | None:
    """The day's poem, from the first view at dusk until the user has settled it."""
    day = store.days.get(logical_day(now))
    if phase is not Phase.DUSK or (day is not None and day.poem_shown_at is not None):
        return None
    return poem_for(logical_day(now), load_poems())


class PoemService:
    def __init__(self, store: Store, clock: Clock) -> None:
        self._store = store
        self._clock = clock

    def settle(self) -> None:
        """The poem was read and closed: it does not come back today."""
        now = self._clock.now()
        today = logical_day(now)
        day = self._store.days.get(today) or Day(logical_day=today)
        self._store.days.save(replace(day, poem_shown_at=now), now)
