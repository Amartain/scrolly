"""A clock for one phase of a Seclusion run: timestamps, computed and never counted. Pure."""

from dataclasses import dataclass, replace
from datetime import datetime, timedelta

FOCUS_MAX_MIN = 120
BREAK_MAX_MIN = 60
CYCLES_MAX = 12
RATIO_MAX = 10


class RunError(ValueError):
    """A setting outside its limits, or an action the run cannot take now."""


def check_range(value: int, low: int, high: int, what: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not low <= value <= high:
        raise RunError(f"{what} must be a whole number from {low} to {high}")
    return value


@dataclass(frozen=True)
class RunClock:
    started_at: datetime | None = None
    accumulated_s: int = 0

    @property
    def running(self) -> bool:
        return self.started_at is not None


def run_elapsed(clock: RunClock, now: datetime) -> int:
    running = 0
    if clock.started_at is not None:
        running = max(0, int((now - clock.started_at).total_seconds()))
    return clock.accumulated_s + running


def run_start(clock: RunClock, now: datetime) -> RunClock:
    """A clock that is already running keeps its original start."""
    return clock if clock.running else replace(clock, started_at=now)


def run_pause(clock: RunClock, now: datetime) -> RunClock:
    if not clock.running:
        return clock
    return RunClock(None, run_elapsed(clock, now))


def reached_at(clock: RunClock, limit_s: int, now: datetime) -> datetime | None:
    """The moment a running clock reached `limit_s`, or None if it has not got there yet."""
    if clock.started_at is None or run_elapsed(clock, now) < limit_s:
        return None
    return clock.started_at + timedelta(seconds=limit_s - clock.accumulated_s)
