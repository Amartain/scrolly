"""The Golden Core Equilibrium: a hand-estimated cognitive-energy ledger. Pure, no IO.

Every threshold is relative to the day's start. Nothing here blocks the user: the curve only
decides how tomorrow begins (see docs/features.md, "The Golden Core Equilibrium").
"""

import math
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date, timedelta

from scrolly.domain.models import OPEN_STATES, OriginType, Trial, TrialState

BASE_START = 100
FLOOR_START = 10
OVERRIDE_CAP = 60
BONUS_CAP = 30
REDLINE_SPAN = 100
LINEAR_SPAN = 30
MAX_STRAIN = 90
RECOVERY_PER_DAY = 30
QI_PER_TRIAL_MAX = 100
HISTORY_DAYS = 7

# The curve rises from LINEAR_SPAN toward MAX_STRAIN: 62 Qi on (192 at a start of 100) it is 89.
_STEEPNESS = math.log(MAX_STRAIN - LINEAR_SPAN) / 62


class QiError(ValueError):
    """A Qi value that cannot be used. The message is shown to the user."""


@dataclass(frozen=True)
class QiDay:
    """A past day the Golden Core was used: the start the user chose and what was spent."""

    day: date
    start: int
    spent: int


@dataclass(frozen=True)
class QiOutlook:
    """How today begins: the strain carried in, the suggested start and what the user may choose."""

    strain: int
    start: int
    low: int
    high: int


def parse_qi(text: str) -> int | None:
    """Qi from a whole number 0-100, or blank (None)."""
    cleaned = text.strip()
    if not cleaned:
        return None
    if not cleaned.isdigit() or int(cleaned) > QI_PER_TRIAL_MAX:
        raise QiError(f"Qi is a whole number from 0 to {QI_PER_TRIAL_MAX}")
    return int(cleaned)


@dataclass(frozen=True)
class GaugeFill:
    """Qi in each zone of the gauge: calm (to the start), surge (next stretch), redline (rest)."""

    calm: int
    surge: int
    redline: int


def redline(start: int) -> int:
    return start + REDLINE_SPAN


def strain_for(spent: int, start: int) -> int:
    """How much tomorrow's start is lowered by today's spending."""
    over = spent - start
    if over <= 0:
        return 0
    if over <= LINEAR_SPAN:
        return over
    if over >= REDLINE_SPAN:
        return MAX_STRAIN
    gap = over - LINEAR_SPAN
    return round(MAX_STRAIN - (MAX_STRAIN - LINEAR_SPAN) * math.exp(-_STEEPNESS * gap))


def effective_qi(trial: Trial) -> int:
    """Qi a trial counts for: what was recorded when it was conquered, else the estimate."""
    if trial.state is TrialState.DONE and trial.qi_actual is not None:
        return trial.qi_actual
    return trial.qi_expected or 0


def _value(trial: Trial) -> int:
    """Qi a trial costs, or minus what a Restorative Art restores."""
    qi = effective_qi(trial)
    return -qi if trial.origin_type is OriginType.RESTORATIVE_ART else qi


def _net(trials: Sequence[Trial], states: frozenset[TrialState]) -> int:
    return max(0, sum(_value(t) for t in trials if t.state in states))


def spent(trials: Sequence[Trial]) -> int:
    """Qi really used: conquered trials only, at the Qi recorded for each."""
    return _net(trials, frozenset({TrialState.DONE}))


def planned(trials: Sequence[Trial]) -> int:
    """Qi the scroll is expected to use: conquered and still open trials."""
    return _net(trials, OPEN_STATES | {TrialState.DONE})


def _bounds(start: int, forced: bool) -> tuple[int, int]:
    if forced:
        return FLOOR_START, FLOOR_START
    return FLOOR_START, max(start, OVERRIDE_CAP)


def outlook(history: Sequence[QiDay], today: date) -> QiOutlook:
    """Walk the recent days one by one. Unused days restore, and they carry no consequence."""
    by_day = {entry.day: entry for entry in history}
    first = max(min(by_day, default=today), today - timedelta(days=HISTORY_DAYS))
    strain, suggested, forced = 0, BASE_START, False
    day = first
    while day < today:
        entry = by_day.get(day) or QiDay(day, suggested, 0)
        recovering = strain > 0
        strain = max(strain_for(entry.spent, entry.start), strain - RECOVERY_PER_DAY)
        bonus = 0 if recovering or strain > 0 else min(BONUS_CAP, max(0, entry.start - entry.spent))
        forced = entry.spent > redline(entry.start)
        suggested = FLOOR_START if forced else max(FLOOR_START, BASE_START - strain) + bonus
        day += timedelta(days=1)
    low, high = _bounds(suggested, forced)
    return QiOutlook(strain=strain, start=suggested, low=low, high=high)


def next_start(strain: int, start: int, planned_qi: int) -> int:
    """Preview of tomorrow's start if today goes as planned (the same step the walk takes)."""
    carried = max(strain_for(planned_qi, start), strain - RECOVERY_PER_DAY)
    if planned_qi > redline(start):
        return FLOOR_START
    bonus = 0 if strain > 0 or carried > 0 else min(BONUS_CAP, max(0, start - planned_qi))
    return max(FLOOR_START, BASE_START - carried) + bonus


def choose_start(value: int, available: QiOutlook) -> int:
    if not available.low <= value <= available.high:
        raise QiError(f"Today's core can begin between {available.low} and {available.high} Qi")
    return value


def gauge_fill(value: int, start: int) -> GaugeFill:
    """How a Qi value fills the three zones of a day that begins at `start`."""
    surge_end = start + LINEAR_SPAN
    return GaugeFill(
        calm=min(value, start),
        surge=max(0, min(value, surge_end) - start),
        redline=max(0, min(value, redline(start)) - surge_end),
    )
