"""Time beside: trials run in Parallel Flow, next to the one at hand. Pure, no IO.

A trial run beside another keeps its own time, so the day's Essence (the sum of every trial's time)
can be more than the hours really sat. These rules say how much of it ran beside, beside which
trial, and how long the day's focus took on the clock.
"""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime

from scrolly.domain.segments import Discipline, Segment


@dataclass(frozen=True)
class Beside:
    minutes: int
    partner_id: str | None  # the trial it ran beside the longest, if any


def _span(segment: Segment, now: datetime) -> tuple[datetime, datetime]:
    return segment.started_at, segment.ended_at or now


def _seconds(start: datetime, end: datetime) -> float:
    return max(0.0, (end - start).total_seconds())


def _overlap(a: Segment, b: Segment, now: datetime) -> float:
    (a0, a1), (b0, b1) = _span(a, now), _span(b, now)
    return _seconds(max(a0, b0), min(a1, b1))


def time_beside(segments: Mapping[str, Sequence[Segment]], now: datetime) -> dict[str, Beside]:
    """For every trial with time run beside another: its minutes beside and its partner."""
    main = {
        trial_id: [s for s in runs if s.discipline is not Discipline.PARALLEL]
        for trial_id, runs in segments.items()
    }
    result: dict[str, Beside] = {}
    for trial_id, runs in segments.items():
        parallel = [s for s in runs if s.discipline is Discipline.PARALLEL]
        if not parallel:
            continue
        seconds = sum(_seconds(*_span(s, now)) for s in parallel)
        shared = {
            other: sum(_overlap(p, m, now) for p in parallel for m in theirs)
            for other, theirs in main.items()
            if other != trial_id
        }
        partner = max(shared, key=lambda other: shared[other], default=None)
        result[trial_id] = Beside(
            minutes=round(seconds / 60),
            partner_id=partner if partner is not None and shared[partner] > 0 else None,
        )
    return result


def focus_minutes(segments: Sequence[Segment], now: datetime) -> int:
    """The clock time of all the day's segments together: overlapping runs count once."""
    spans = sorted(_span(s, now) for s in segments)
    total = 0.0
    current: tuple[datetime, datetime] | None = None
    for start, end in spans:
        if current is None or start > current[1]:
            if current is not None:
                total += _seconds(*current)
            current = (start, end)
        else:
            current = (current[0], max(current[1], end))
    if current is not None:
        total += _seconds(*current)
    return round(total / 60)
