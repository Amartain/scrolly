from dataclasses import dataclass, replace
from datetime import datetime

from scrolly.domain import queue
from scrolly.domain.advisor import advisor_due, postponable_mandates, remaining_expected_min
from scrolly.domain.appearance import Phase
from scrolly.domain.logical_day import logical_day
from scrolly.domain.models import Day
from scrolly.domain.sunset import SunsetPrefs
from scrolly.ports import Clock, Store
from scrolly.services.sunset import settle_day


@dataclass(frozen=True)
class AdvisorView:
    due: bool
    mandates: int  # waiting Mandates the advisor could postpone
    silenced: bool  # "not again today" was chosen


def build_advisor(store: Store, now: datetime, prefs: SunsetPrefs, phase: Phase) -> AdvisorView:
    today = logical_day(now)
    day = store.days.get(today)
    sealed = day is not None and day.first_sealed_at is not None
    trials = store.trials.list_for_day(today) if sealed else []
    silenced = day is not None and day.advisor_silenced
    due = advisor_due(now, prefs, phase, remaining_expected_min(trials), silenced)
    return AdvisorView(due=due, mandates=len(postponable_mandates(trials)), silenced=silenced)


class AdvisorService:
    def __init__(self, store: Store, clock: Clock) -> None:
        self._store = store
        self._clock = clock

    def silence(self, silenced: bool) -> None:
        """Not again today (or, from Settings, let the advisor speak again)."""
        now = self._clock.now()
        today = logical_day(now)
        day = self._store.days.get(today) or Day(logical_day=today)
        self._store.days.save(replace(day, advisor_silenced=silenced), now)

    def postpone_mandates(self) -> None:
        """Send the waiting Mandates to the Horizon. One word of advice is enough for the day."""
        now = self._clock.now()
        today = logical_day(now)
        trials = self._store.trials.list_for_day(today)
        changed, horizon = queue.postpone_mandates(trials, self._store.horizon.list_all(), now)
        if changed:
            self._store.horizon.replace_all(horizon, now)
            self._store.trials.save(changed, now)
            settle_day(self._store, now)
        self.silence(True)
