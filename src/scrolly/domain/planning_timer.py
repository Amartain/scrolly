"""The quiet timer of planning: time spent thinking, estimating and weighing, kept for each day.

Like the Immediate Trial's timer, it is two timestamps and a total, so a closed tab, a sleeping
laptop or a crash loses nothing: the time is worked out from them, never counted. Pure.
"""

from dataclasses import replace
from datetime import datetime

from scrolly.domain.models import Day


def elapsed_seconds(day: Day, now: datetime) -> int:
    """The total so far, with the running stretch if the timer is on."""
    running = 0
    if day.planning_started_at is not None:
        running = max(0, int((now - day.planning_started_at).total_seconds()))
    return day.planning_accumulated_s + running


def is_running(day: Day) -> bool:
    return day.planning_started_at is not None


def start(day: Day, now: datetime) -> Day:
    """Begin a stretch. A timer already running keeps its start."""
    if day.planning_started_at is not None:
        return day
    return replace(day, planning_started_at=now)


def pause(day: Day, now: datetime) -> Day:
    """Fold a running stretch into the total. A timer that is not running is unchanged."""
    if day.planning_started_at is None:
        return day
    return replace(day, planning_started_at=None, planning_accumulated_s=elapsed_seconds(day, now))


def reset(day: Day) -> Day:
    """The user chose to zero it. Neutral: nothing else is touched."""
    return replace(day, planning_started_at=None, planning_accumulated_s=0)


def close_at(day: Day, end: datetime) -> Day:
    """A timer left running when its day ended stops at that end, not at whenever it is noticed."""
    return pause(day, end)
