"""The trials of a sealed day, as the services that act on them look them up."""

from collections.abc import Sequence
from datetime import date

from scrolly.domain.day_flow import TrialError
from scrolly.domain.models import Trial
from scrolly.ports import Store


def sealed_trials(store: Store, day: date) -> list[Trial]:
    record = store.days.get(day)
    if record is None or record.first_sealed_at is None:
        raise TrialError("The day has not begun yet")
    return store.trials.list_for_day(day)


def find_trial(trials: Sequence[Trial], trial_id: str) -> Trial:
    trial = next((t for t in trials if t.id == trial_id), None)
    if trial is None:
        raise TrialError("That trial is not on today's scroll")
    return trial
