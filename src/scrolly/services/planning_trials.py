import uuid
from datetime import date, datetime
from typing import Literal

from scrolly.domain.logical_day import logical_day
from scrolly.domain.models import PlanningDraft, Trial
from scrolly.domain.planning import (
    PlanningError,
    dismiss,
    next_position,
    reorder,
    set_estimate,
    set_mandate,
    set_qi,
    trial_from_art,
    trial_from_horizon,
    trial_from_line,
    unstage,
)
from scrolly.ports import Clock, Store
from scrolly.services.planning import planning_trials


class PlanningTrialsService:
    """Edits to the trials on a scroll that is still being planned."""

    def __init__(self, store: Store, clock: Clock) -> None:
        self._store = store
        self._clock = clock

    @property
    def _now(self) -> datetime:
        return self._clock.now()

    @property
    def _today(self) -> date:
        return logical_day(self._now)

    def _open_draft(self) -> PlanningDraft:
        draft = self._store.drafts.get()
        if draft is None:
            raise PlanningError("Planning has not started")
        return draft

    def _trial(self, trial_id: str) -> Trial:
        self._open_draft()
        for trial in planning_trials(self._store, self._today):
            if trial.id == trial_id:
                return trial
        raise PlanningError("That trial is not on the scroll")

    def _position(self) -> int:
        return next_position(planning_trials(self._store, self._today))

    def summon(self, source: Literal["horizon", "art"], item_id: str) -> None:
        self._open_draft()
        new_id, position = str(uuid.uuid4()), self._position()
        if source == "horizon":
            items = self._store.horizon.list_all()
            item = next((i for i in items if i.id == item_id), None)
            if item is None:
                raise PlanningError("That item is no longer on the Horizon")
            trial = trial_from_horizon(new_id, item, self._today, position)
            remaining = [i for i in items if i.id != item_id]
            self._store.horizon.replace_all(remaining, self._now)
        else:
            art = next((a for a in self._store.arts.list_all() if a.id == item_id), None)
            if art is None:
                raise PlanningError("That Art does not exist")
            trial = trial_from_art(new_id, art, self._today, position)
        self._store.trials.save([trial], self._now)

    def unstage(self, trial_id: str) -> None:
        trial = self._trial(trial_id)
        horizon = unstage(trial, self._store.horizon.list_all())
        self._store.horizon.replace_all(horizon, self._now)
        self._store.trials.delete([trial.id])

    def add(self, title: str) -> None:
        self._open_draft()
        cleaned = title.strip()
        if not cleaned:
            raise PlanningError("A trial needs a title")
        trial = trial_from_line(str(uuid.uuid4()), cleaned, self._today, self._position())
        self._store.trials.save([trial], self._now)

    def update(
        self,
        trial_id: str,
        estimate: str | None,
        is_mandate: bool | None,
        qi: str | None = None,
    ) -> None:
        trial = self._trial(trial_id)
        if is_mandate is not None:
            trial = set_mandate(trial, is_mandate)
        if estimate is not None:
            trial = set_estimate(trial, estimate)
        if qi is not None:
            trial = set_qi(trial, qi)
        self._store.trials.save([trial], self._now)

    def dismiss(self, trial_id: str) -> None:
        trial = self._trial(trial_id)
        gone, horizon = dismiss(trial, self._store.horizon.list_all())
        self._store.horizon.replace_all(horizon, self._now)
        self._store.trials.save([gone], self._now)

    def reorder(self, ids: list[str]) -> None:
        self._open_draft()
        ordered = reorder(planning_trials(self._store, self._today), ids)
        self._store.trials.save(ordered, self._now)
