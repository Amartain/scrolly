from dataclasses import dataclass
from datetime import date, datetime

from scrolly.domain import planning_timer as timer
from scrolly.domain.logical_day import logical_day, logical_day_end
from scrolly.domain.models import Day
from scrolly.ports import Clock, Store


@dataclass(frozen=True)
class PlanningTimerView:
    """Time spent planning today as of the view. The browser animates from here."""

    elapsed_s: int
    running: bool


def build_planning_timer(store: Store, now: datetime) -> PlanningTimerView:
    day = store.days.get(logical_day(now)) or Day(logical_day=logical_day(now))
    return PlanningTimerView(timer.elapsed_seconds(day, now), timer.is_running(day))


def close_stale_timers(store: Store, today: date, now: datetime) -> None:
    """A planning timer left running when its day ended stops at that day's end."""
    for day in store.days.list_all():
        if day.logical_day < today and timer.is_running(day):
            closed = timer.close_at(day, logical_day_end(day.logical_day, now))
            store.days.save(closed, now)


class PlanningTimerService:
    def __init__(self, store: Store, clock: Clock) -> None:
        self._store = store
        self._clock = clock

    def _change(self, change: str) -> None:
        now = self._clock.now()
        today = logical_day(now)
        day = self._store.days.get(today) or Day(logical_day=today)
        if change == "start":
            day = timer.start(day, now)
        elif change == "pause":
            day = timer.pause(day, now)
        else:
            day = timer.reset(day)
        self._store.days.save(day, now)

    def start(self) -> None:
        self._change("start")

    def pause(self) -> None:
        self._change("pause")

    def reset(self) -> None:
        self._change("reset")
