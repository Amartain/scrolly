"""The overrun advisor: one gentle word when the open trials would run past sunset. Pure."""

from collections.abc import Sequence
from datetime import datetime, timedelta

from scrolly.domain.appearance import Phase
from scrolly.domain.day_budget import sunset_at
from scrolly.domain.models import OPEN_STATES, Trial, TrialState
from scrolly.domain.sunset import SunsetPrefs


def remaining_expected_min(trials: Sequence[Trial]) -> int:
    """Minutes estimated for the open trials. A trial without an estimate adds nothing."""
    return sum(t.essence_expected_min or 0 for t in trials if t.state in OPEN_STATES)


def advisor_due(
    now: datetime, prefs: SunsetPrefs, phase: Phase, remaining_min: int, silenced: bool
) -> bool:
    """By day, with a sunset kept, when the open trials would end after it, and not yet silenced."""
    if silenced or not prefs.enabled or phase is Phase.DUSK or remaining_min <= 0:
        return False
    return now + timedelta(minutes=remaining_min) > sunset_at(now, prefs.at)


def postponable_mandates(trials: Sequence[Trial]) -> list[Trial]:
    """The Mandates waiting in the queue, top first. The Immediate Trial is never one of them."""
    waiting = [t for t in trials if t.state is TrialState.REMAINING and t.is_mandate]
    return sorted(waiting, key=lambda t: t.position)
