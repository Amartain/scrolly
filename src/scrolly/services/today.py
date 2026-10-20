import uuid
from datetime import date, datetime
from typing import Literal

from scrolly.domain import day_flow, queue, timer
from scrolly.domain.day_flow import TrialError
from scrolly.domain.logical_day import logical_day
from scrolly.domain.models import Trial, TrialState
from scrolly.domain.planning import (
    PlanningError,
    next_position,
    set_mandate,
    trial_from_art,
    trial_from_horizon,
)
from scrolly.domain.uniqueness import require_free_trial_title
from scrolly.ports import Clock, Store
from scrolly.services.sunset import settle_day


class TodayService:
    """What the user does to the trials of a sealed day: time them, conquer them, let them go."""

    def __init__(self, store: Store, clock: Clock) -> None:
        self._store = store
        self._clock = clock

    @property
    def _now(self) -> datetime:
        return self._clock.now()

    @property
    def _today(self) -> date:
        return logical_day(self._now)

    def _trials(self) -> list[Trial]:
        day = self._store.days.get(self._today)
        if day is None or day.first_sealed_at is None:
            raise TrialError("The day has not begun yet")
        return self._store.trials.list_for_day(self._today)

    def _trial(self, trial_id: str) -> Trial:
        trial = next((t for t in self._trials() if t.id == trial_id), None)
        if trial is None:
            raise TrialError("That trial is not on today's scroll")
        return trial

    def _timed(self, trial_id: str) -> Trial:
        trial = self._trial(trial_id)
        if trial.state is not TrialState.IMMEDIATE:
            raise TrialError("Only the Immediate Trial has a timer")
        return trial

    def _promote(self) -> None:
        promoted = day_flow.promote_next(self._store.trials.list_for_day(self._today))
        self._store.trials.save(promoted, self._now)

    def start_timer(self, trial_id: str) -> None:
        self._store.trials.save([timer.start(self._timed(trial_id), self._now)], self._now)

    def pause_timer(self, trial_id: str) -> None:
        self._store.trials.save([timer.pause(self._timed(trial_id), self._now)], self._now)

    def reset_timer(self, trial_id: str) -> None:
        self._store.trials.save([timer.reset(self._timed(trial_id))], self._now)

    def conquer(self, trial_id: str) -> None:
        self._store.trials.save([day_flow.conquer(self._trial(trial_id), self._now)], self._now)
        self._promote()
        settle_day(self._store, self._now)

    def postpone(self, trial_id: str) -> None:
        gone, horizon = day_flow.postpone(
            self._trial(trial_id), self._store.horizon.list_all(), self._now
        )
        self._store.horizon.replace_all(horizon, self._now)
        self._store.trials.save([gone], self._now)
        self._promote()
        settle_day(self._store, self._now)

    def abandon(self, trial_id: str) -> None:
        self._store.trials.save([day_flow.abandon(self._trial(trial_id), self._now)], self._now)
        self._promote()
        settle_day(self._store, self._now)

    def revive(self, trial_id: str) -> None:
        trial = self._trial(trial_id)
        self._store.trials.save([day_flow.revive(trial, self._trials())], self._now)

    def update(
        self,
        trial_id: str,
        title: str | None = None,
        is_mandate: bool | None = None,
        qi: str | None = None,
        estimate: str | None = None,
    ) -> None:
        """Only the fields that are given change."""
        trial = self._trial(trial_id)
        day_flow.require_editable(trial)
        if title is not None:
            self._require_free(title, trial.id)
            trial = day_flow.rename(trial, title, self._store.arts.list_all())
        if is_mandate is not None:
            trial = set_mandate(trial, is_mandate)
        if estimate is not None:
            trial = day_flow.set_estimate(trial, estimate)
        if qi is not None:
            trial = day_flow.set_estimated_qi(trial, qi)
        self._store.trials.save([trial], self._now)

    def _require_free(self, title: str, except_id: str | None = None) -> None:
        horizon = self._store.horizon.list_all()
        arts = self._store.arts.list_all()
        require_free_trial_title(title, horizon, self._trials(), arts, except_id=except_id)

    def scribe(self, title: str, estimate: str = "", qi: str = "") -> None:
        self._require_free(title)
        arts = self._store.arts.list_all()
        trial = queue.scribe(
            str(uuid.uuid4()), title, estimate, qi, self._today, self._trials(), arts
        )
        self._store.trials.save([trial], self._now)

    def promote(self, trial_id: str) -> None:
        trial, trials = self._trial(trial_id), self._trials()
        self._store.trials.save(queue.promote(trial, trials, self._now), self._now)

    def reorder(self, ids: list[str]) -> None:
        ordered = queue.reorder_remaining(self._trials(), ids)
        self._store.trials.save(ordered, self._now)

    def summon(self, source: Literal["horizon", "art"], item_id: str) -> None:
        """Bring a Horizon item (it leaves the Horizon) or a copy of an Art onto the day's queue."""
        trials = self._trials()
        new_id, position = str(uuid.uuid4()), next_position(trials)
        if source == "horizon":
            items = self._store.horizon.list_all()
            item = next((i for i in items if i.id == item_id), None)
            if item is None:
                raise PlanningError("That item is no longer on the Horizon")
            trial = trial_from_horizon(new_id, item, self._today, position)
            self._store.horizon.replace_all([i for i in items if i.id != item_id], self._now)
        else:
            art = next((a for a in self._store.arts.list_all() if a.id == item_id), None)
            if art is None:
                raise PlanningError("That Art does not exist")
            trial = trial_from_art(new_id, art, self._today, position)
        self._store.trials.save([trial], self._now)
        self._promote()
