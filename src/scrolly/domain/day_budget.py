"""How much of the day's light the planned trials use. Pure, no IO."""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, time, timedelta

from scrolly.domain.logical_day import ROLLOVER_HOUR, logical_day
from scrolly.domain.models import OPEN_STATES, Trial

DEFAULT_SUNSET = time(21, 0)


@dataclass(frozen=True)
class DayBudget:
    trial_count: int
    planned_min: int
    mandate_min: int
    mortal_min: int
    unestimated_count: int
    light_min: int | None  # None once the sun has set
    beyond_light_min: int


def sunset_at(now: datetime, sunset: time) -> datetime:
    """When the sun sets on the logical day `now` belongs to (after midnight if set that late)."""
    moment = datetime.combine(logical_day(now), sunset, tzinfo=now.tzinfo)
    return moment + timedelta(days=1) if sunset < time(ROLLOVER_HOUR) else moment


def light_left(now: datetime, sunset: time) -> int | None:
    """Whole minutes of light left, or None after sunset."""
    seconds = (sunset_at(now, sunset) - now).total_seconds()
    return None if seconds <= 0 else int(seconds // 60)


def day_budget(trials: Sequence[Trial], now: datetime, sunset: time) -> DayBudget:
    """The open trials against the light left. Trials without an estimate are counted, not timed."""
    open_trials = [t for t in trials if t.state in OPEN_STATES]
    estimates = [(t, t.essence_expected_min or 0) for t in open_trials]
    planned = sum(minutes for _, minutes in estimates)
    mandate = sum(minutes for t, minutes in estimates if t.is_mandate)
    light = light_left(now, sunset)
    return DayBudget(
        trial_count=len(open_trials),
        planned_min=planned,
        mandate_min=mandate,
        mortal_min=planned - mandate,
        unestimated_count=sum(1 for t in open_trials if t.essence_expected_min is None),
        light_min=light,
        beyond_light_min=0 if light is None else max(0, planned - light),
    )
