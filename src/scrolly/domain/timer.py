from dataclasses import replace
from datetime import datetime

from scrolly.domain.models import Trial


def elapsed_seconds(trial: Trial, now: datetime) -> int:
    """Accumulated time plus the running segment. Computed, never tick-counted."""
    running = 0
    if trial.timer_started_at is not None:
        running = max(0, int((now - trial.timer_started_at).total_seconds()))
    return trial.timer_accumulated_s + running


def pause(trial: Trial, now: datetime) -> Trial:
    """Fold a running segment into the total. A timer that is not running is unchanged."""
    if trial.timer_started_at is None:
        return trial
    return replace(
        trial,
        timer_started_at=None,
        timer_paused_at=now,
        timer_accumulated_s=elapsed_seconds(trial, now),
    )


def start(trial: Trial, now: datetime) -> Trial:
    """Begin a new running segment. A timer that is already running keeps its original start."""
    if trial.timer_started_at is not None:
        return trial
    return replace(trial, timer_started_at=now, timer_paused_at=None)


def reset(trial: Trial) -> Trial:
    return replace(trial, timer_started_at=None, timer_paused_at=None, timer_accumulated_s=0)


def timer_ran(trial: Trial) -> bool:
    return trial.timer_started_at is not None or trial.timer_accumulated_s > 0


def actual_minutes(trial: Trial, now: datetime) -> int | None:
    """Minutes a finished trial records: the timer (at least 1) if it ran, else the estimate."""
    if not timer_ran(trial):
        return trial.essence_expected_min
    return max(1, round(elapsed_seconds(trial, now) / 60))
