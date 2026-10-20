"""The two motivation charts: Cumulative Momentum and the 7-day Rhythm. Pure.

These charts show the user their momentum and rhythm. They are not analytics: Rhythm bars use a
compressed scale so one big day never dwarfs the rest, and the figures are rounded for the eye.
"""

import math
import random
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date, timedelta
from enum import StrEnum

from scrolly.domain.models import Trial, TrialState
from scrolly.domain.qi import effective_qi

RHYTHM_DAYS = 7
MIN_BAR_PCT = 25
MAX_POINTS = 60


class Metric(StrEnum):
    TRIALS = "trials"
    ESSENCE = "essence"
    QI = "qi"


@dataclass(frozen=True)
class Point:
    day: date
    value: int


@dataclass(frozen=True)
class Bar:
    day: date
    value: int
    height_pct: int  # 0 on a rest day, else MIN_BAR_PCT to 100
    is_rest: bool


def _value(trial: Trial, metric: Metric) -> int:
    """What one conquered trial adds. Qi counts what was recorded, restored or spent alike."""
    if metric is Metric.TRIALS:
        return 1
    if metric is Metric.ESSENCE:
        return trial.essence_actual_min or 0
    return effective_qi(trial)


def daily_totals(trials: Sequence[Trial], metric: Metric) -> dict[date, int]:
    """Per logical day, the total of what was conquered that day (Essence also counts the
    minutes timed on a trial that was let go)."""
    spent = {TrialState.DONE, TrialState.LOST} if metric is Metric.ESSENCE else {TrialState.DONE}
    totals: dict[date, int] = {}
    for trial in trials:
        if trial.state in spent:
            totals[trial.logical_day] = totals.get(trial.logical_day, 0) + _value(trial, metric)
    return totals


def momentum(trials: Sequence[Trial], metric: Metric) -> list[Point]:
    """All-time running total, kept only on days it rose, so every point is higher than the last."""
    total, points = 0, []
    for day, added in sorted(daily_totals(trials, metric).items()):
        if added > 0:
            total += added
            points.append(Point(day, total))
    return points


def thin(points: Sequence[Point], limit: int = MAX_POINTS) -> list[Point]:
    """At most `limit` points for drawing: the first and last always stay, the rest are spread."""
    if len(points) <= limit:
        return list(points)
    last = len(points) - 1
    return [points[round(i * last / (limit - 1))] for i in range(limit)]


def _height_pct(value: int, biggest: int) -> int:
    """A log scale with a floor, so a small day still shows next to a big one."""
    span = MIN_BAR_PCT + (100 - MIN_BAR_PCT) * math.log1p(value) / math.log1p(biggest)
    return round(span)


def rhythm(trials: Sequence[Trial], today: date, metric: Metric) -> list[Bar]:
    """The 7 calendar days ending today, oldest first. A day with nothing is a rest day."""
    totals = daily_totals(trials, metric)
    days = [today - timedelta(days=RHYTHM_DAYS - 1 - i) for i in range(RHYTHM_DAYS)]
    biggest = max((totals.get(d, 0) for d in days), default=0)
    return [
        Bar(d, totals.get(d, 0), _height_pct(totals[d], biggest), False)
        if totals.get(d, 0) > 0
        else Bar(d, 0, 0, True)
        for d in days
    ]


def placeholder_momentum(today: date) -> list[Point]:
    """A fixed rising shape for a fresh scroll; the interface shows it under fog."""
    rng = random.Random(7)
    value, points = 0, []
    for step in range(12):
        value += rng.randint(2, 9)
        points.append(Point(today - timedelta(days=(11 - step) * 3), value))
    return points


def placeholder_rhythm(today: date) -> list[Bar]:
    """A fixed week with one rest day, shown under fog."""
    heights = [55, 80, 0, 100, 45, 70, 90]
    days = [today - timedelta(days=RHYTHM_DAYS - 1 - i) for i in range(RHYTHM_DAYS)]
    return [Bar(d, h // 10, h, h == 0) for d, h in zip(days, heights, strict=True)]
