from collections.abc import Sequence
from dataclasses import dataclass, replace
from datetime import date, datetime

from scrolly.domain.horizon import return_to_horizon
from scrolly.domain.models import OPEN_STATES, HorizonItem, Trial, TrialState
from scrolly.domain.timer import pause


@dataclass(frozen=True)
class RolloverResult:
    changed: list[Trial]
    horizon: list[HorizonItem]


def rollover(
    trials: Sequence[Trial],
    horizon: Sequence[HorizonItem],
    today: date,
    now: datetime,
    held_day: date | None = None,
) -> RolloverResult:
    """Settle every unfinished trial from before `today`.

    A Mortal Trial is lost to time. A Heavenly Mandate returns to the top of the
    Horizon (deduplicated). Finished and postponed trials stay as they are, so a
    second run changes nothing. The `held_day` (the scroll open in Seclusion past 04:00)
    is left alone until the user steps out.
    """
    stale = sorted(
        (
            t
            for t in trials
            if t.state in OPEN_STATES and t.logical_day < today and t.logical_day != held_day
        ),
        key=lambda t: (t.logical_day, t.position),
    )
    changed: list[Trial] = []
    items = list(horizon)
    # Newest first, so the oldest mandate ends on top and the original order is kept.
    for trial in reversed(stale):
        stopped = pause(trial, now)
        if trial.is_mandate:
            items = return_to_horizon(items, stopped)
            changed.append(replace(stopped, state=TrialState.RETURNED))
        else:
            changed.append(replace(stopped, state=TrialState.LOST))
    return RolloverResult(changed=changed, horizon=items)
