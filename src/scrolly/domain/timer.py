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
