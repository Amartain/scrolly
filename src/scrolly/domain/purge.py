"""Purge Today's Scroll: clear what is still open today. Pure."""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime

from scrolly.domain.horizon import return_to_horizon
from scrolly.domain.models import OPEN_STATES, HorizonItem, OriginType, Trial, TrialState
from scrolly.domain.timer import pause


@dataclass(frozen=True)
class Purged:
    removed: list[str]  # ids of the trials to delete
    horizon: list[HorizonItem]


def purge_today(trials: Sequence[Trial], horizon: Sequence[HorizonItem], now: datetime) -> Purged:
    """Remove today's open trials. Conquered, postponed and fallen ones stay.

    A Heavenly Mandate and anything summoned from the Horizon goes back to it with the time worked
    so far; a Mortal Trial from the dump, and any Art instance, is simply removed.
    """
    order = {TrialState.IMMEDIATE: 0, TrialState.REMAINING: 1}
    open_trials = sorted(
        (t for t in trials if t.state in OPEN_STATES), key=lambda t: (order[t.state], t.position)
    )
    items = list(horizon)
    # Last first, so the one that was on top ends on top.
    for trial in reversed(open_trials):
        returns = trial.is_mandate or trial.origin_type is OriginType.HORIZON
        if trial.art_kind is None and returns:
            items = return_to_horizon(items, pause(trial, now))
    return Purged(removed=[t.id for t in open_trials], horizon=items)
