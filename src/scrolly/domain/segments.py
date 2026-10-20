"""Time as segments: one continuous run of one discipline on one trial. Pure, no IO.

A trial's own timer still holds its total; segments say how that time was spent and on which day.
"""

from collections.abc import Sequence
from dataclasses import dataclass, replace
from datetime import date, datetime
from enum import StrEnum

from scrolly.domain.logical_day import logical_day, logical_day_end


class Discipline(StrEnum):
    DASHBOARD = "dashboard"
    INCENSE = "incense"
    PULSE = "pulse"
    FLOW = "flow"


@dataclass(frozen=True)
class Segment:
    id: str
    trial_id: str
    discipline: Discipline
    started_at: datetime
    ended_at: datetime | None = None


def open_segment(segment_id: str, trial_id: str, discipline: Discipline, now: datetime) -> Segment:
    return Segment(segment_id, trial_id, discipline, started_at=now)


def close_segment(segment: Segment, now: datetime) -> Segment:
    """End a running segment. One that has ended stays as it was."""
    if segment.ended_at is not None:
        return segment
    return replace(segment, ended_at=max(now, segment.started_at))


def seconds_by_day(segments: Sequence[Segment], now: datetime) -> dict[date, int]:
    """Seconds per logical day. A segment that crosses 04:00 is split there, by timestamp."""
    totals: dict[date, int] = {}
    for segment in segments:
        end = segment.ended_at or now
        cursor = segment.started_at
        while cursor < end:
            day = logical_day(cursor)
            stop = min(end, logical_day_end(day, cursor))
            totals[day] = totals.get(day, 0) + int((stop - cursor).total_seconds())
            cursor = stop
    return totals
