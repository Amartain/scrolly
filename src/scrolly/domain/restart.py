"""Restart today: as if the day had not begun. A tool for testing the Serene Peak. Pure."""

from collections.abc import Sequence
from dataclasses import dataclass, replace
from datetime import datetime

from scrolly.domain.horizon import return_to_horizon
from scrolly.domain.models import Day, HorizonItem, OriginType, Trial, TrialState
from scrolly.domain.timer import pause

# Trials that took something off the Horizon and have not given it back.
_CONSUMED = {TrialState.IMMEDIATE, TrialState.REMAINING, TrialState.DONE}


@dataclass(frozen=True)
class Restarted:
    removed: list[str]  # ids of every trial of the day, to delete
    horizon: list[HorizonItem]
    day: Day


def restart_today(
    trials: Sequence[Trial], horizon: Sequence[HorizonItem], day: Day, now: datetime
) -> Restarted:
    """Remove all of today's trials, unseal the day and reset its flags.

    What was called down from the Horizon goes back to it with the time worked. Heavenly Cycles
    fall by one until the day is sealed again. The day's rollover stays done.
    """
    items = list(horizon)
    for trial in reversed(sorted(trials, key=lambda t: t.position)):
        came_from_horizon = trial.origin_type is OriginType.HORIZON and trial.art_kind is None
        if came_from_horizon and trial.state in _CONSUMED:
            items = return_to_horizon(items, pause(trial, now))
    fresh = replace(
        day,
        first_sealed_at=None,
        qi_start=None,
        dusk_override=None,
        advisor_silenced=False,
        poem_shown_at=None,
    )
    return Restarted(removed=[t.id for t in trials], horizon=items, day=fresh)
