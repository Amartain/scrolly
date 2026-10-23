"""What the user does afterwards to a trial of today that is finished or let go: correct the time
and Qi a conquest took, revive it, or summon back one postponed or let go (owner, 2026-10-23)."""

from datetime import date, datetime

from scrolly.domain import day_flow
from scrolly.domain.models import Trial
from scrolly.ports import Clock, Store
from scrolly.services.sealed_day import find_trial, sealed_trials
from scrolly.services.seclusion_state import working_day


class FinishedTrials:
    def __init__(self, store: Store, clock: Clock) -> None:
        self._store = store
        self._clock = clock

    @property
    def _now(self) -> datetime:
        return self._clock.now()

    @property
    def _today(self) -> date:
        return working_day(self._store, self._now)

    def _trials(self) -> list[Trial]:
        return sealed_trials(self._store, self._today)

    def _trial(self, trial_id: str) -> Trial:
        return find_trial(self._trials(), trial_id)

    def set_actual_qi(self, trial_id: str, qi: int) -> None:
        """What the user says a conquered trial took; conquering had recorded the estimate."""
        trial = day_flow.set_actual_qi(self._trial(trial_id), qi)
        self._store.trials.save([trial], self._now)

    def set_actual(self, trial_id: str, text: str) -> None:
        """The user corrects the time a conquered trial took."""
        trial = day_flow.set_actual_minutes(self._trial(trial_id), text)
        self._store.trials.save([trial], self._now)

    def revive(self, trial_id: str) -> None:
        trial = self._trial(trial_id)
        self._store.trials.save([day_flow.revive(trial, self._trials())], self._now)

    def resummon(self, trial_id: str) -> None:
        """A trial postponed or let go today comes back to the scroll."""
        back, horizon = day_flow.resummon(
            self._trial(trial_id), self._trials(), self._store.horizon.list_all()
        )
        self._store.horizon.replace_all(horizon, self._now)
        self._store.trials.save([back], self._now)
