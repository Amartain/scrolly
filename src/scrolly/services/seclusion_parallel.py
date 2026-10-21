"""Parallel Flow: a trial of its own run beside the one at hand, kept apart from the main trial.

The trial keeps its place in Remaining while it runs beside the main one. It has its own timer,
qi and conquest. When the main trial ends, an unfinished parallel one is the next to be promoted.
"""

from dataclasses import dataclass, replace
from datetime import datetime
from typing import Literal

from scrolly.domain import timer
from scrolly.domain.day_flow import TrialError
from scrolly.domain.models import Trial
from scrolly.domain.parallel import Candidate, Source, can_run_beside, find_candidates
from scrolly.domain.segments import Discipline
from scrolly.domain.timer import elapsed_seconds
from scrolly.ports import Clock, Store
from scrolly.services.dashboard_view import TimerView
from scrolly.services.scraps import ScrapService
from scrolly.services.seclusion_state import (
    immediate_trial,
    parallel_trial,
    read_state,
    working_day,
    write_state,
)
from scrolly.services.segments import sync_segments
from scrolly.services.today import TodayService


@dataclass(frozen=True)
class ParallelView:
    trial: Trial
    timer: TimerView


class ParallelControl:
    def __init__(
        self, store: Store, clock: Clock, today: TodayService, scraps: ScrapService
    ) -> None:
        self._store = store
        self._clock = clock
        self._today = today
        self._scraps = scraps

    @property
    def _now(self) -> datetime:
        return self._clock.now()

    def _beside(self) -> Trial:
        trial = parallel_trial(self._store, self._now)
        if trial is None:
            raise TrialError("Nothing runs beside the trial at hand")
        return trial

    def _forget(self) -> None:
        state = read_state(self._store)
        write_state(self._store, replace(state, parallel_id=None), self._now)

    def search(self, query: str) -> list[Candidate]:
        main = immediate_trial(self._store, self._now)
        trials = self._store.trials.list_for_day(working_day(self._store, self._now))
        arts, horizon = self._store.arts.list_all(), self._store.horizon.list_all()
        return find_candidates(query, trials, arts, horizon, None if main is None else main.id)

    def view(self) -> ParallelView | None:
        trial = parallel_trial(self._store, self._now)
        if trial is None:
            return None
        expected = trial.essence_expected_min
        shown = TimerView(
            elapsed_seconds(trial, self._now),
            trial.timer_started_at is not None,
            None if expected is None else expected * 60,
        )
        return ParallelView(trial, shown)

    def pick(self, source: Source | Literal["new"], ref: str) -> None:
        """Take a waiting trial, an Art or a Horizon item (or, `new`, a title) to run beside."""
        main = immediate_trial(self._store, self._now)
        if main is None:
            raise TrialError("There is no trial at hand to run beside")
        if parallel_trial(self._store, self._now) is not None:
            raise TrialError("Only one trial can run beside the one at hand")
        if source == "new":
            trial_id = self._today.scribe(ref)
        elif source == Source.ART:
            trial_id = self._today.summon("art", ref)
        elif source == Source.HORIZON:
            trial_id = self._today.summon("horizon", ref)
        else:
            trial_id = ref
        trials = self._store.trials.list_for_day(working_day(self._store, self._now))
        trial = next((t for t in trials if t.id == trial_id), None)
        if trial is None or not can_run_beside(trial, main.id, None):
            raise TrialError("That trial cannot run beside the one at hand")
        write_state(self._store, replace(read_state(self._store), parallel_id=trial_id), self._now)

    def start(self) -> None:
        trial = self._beside()
        started = timer.start(trial, self._now)
        self._store.trials.save([started], self._now)
        sync_segments(self._store, [started], self._now, Discipline.PARALLEL)
        self._scraps.note_trial(trial.id)

    def pause(self, at: datetime | None = None) -> None:
        """Stepping out pauses it too. Nothing running is left as it is."""
        trial = parallel_trial(self._store, self._now)
        if trial is None or trial.timer_started_at is None:
            return
        stopped = at or self._now
        paused = timer.pause(trial, stopped)
        self._store.trials.save([paused], self._now)
        sync_segments(self._store, [paused], stopped, Discipline.PARALLEL)

    def finish(self, how: Literal["conquered", "abandoned", "postponed"]) -> None:
        """End the parallel trial on its own: the main trial is not touched."""
        trial = self._beside()
        if how == "conquered":
            self._today.conquer(trial.id, beside=True)
        elif how == "abandoned":
            self._today.abandon(trial.id)
        else:
            self._today.postpone(trial.id)
        self._forget()
