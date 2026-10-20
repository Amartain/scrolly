from dataclasses import replace
from datetime import date, datetime

from scrolly.domain.logical_day import logical_day
from scrolly.domain.models import Day
from scrolly.domain.rollover import rollover
from scrolly.ports import Clock, Store
from scrolly.services.planning import abandon_planning
from scrolly.services.planning_timer import close_stale_timers


def run_rollover(store: Store, today: date, now: datetime) -> None:
    """Settle every unfinished trial from before today and save the result."""
    result = rollover(store.trials.list_open_before(today), store.horizon.list_all(), today, now)
    if result.changed:
        store.trials.save(result.changed, now)
        store.horizon.replace_all(result.horizon, now)


class DayService:
    def __init__(self, store: Store, clock: Clock) -> None:
        self._store = store
        self._clock = clock

    def ensure_today(self) -> None:
        """Roll the previous days over once, on the first request of a logical day."""
        now = self._clock.now()
        today = logical_day(now)
        day = self._store.days.get(today) or Day(logical_day=today)
        if day.rolled_over_at is not None:
            return
        draft = self._store.drafts.get()
        if draft is not None and draft.logical_day < today:
            abandon_planning(self._store, draft, now)
        run_rollover(self._store, today, now)
        close_stale_timers(self._store, today, now)
        self._store.days.save(replace(day, rolled_over_at=now), now)
