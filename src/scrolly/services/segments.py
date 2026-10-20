"""Keeps the timer segments in step with the trials' own timers."""

import uuid
from collections.abc import Sequence
from datetime import datetime

from scrolly.domain.models import Trial
from scrolly.domain.segments import Discipline, close_segment, open_segment
from scrolly.ports import Store


def sync_segments(
    store: Store,
    trials: Sequence[Trial],
    now: datetime,
    discipline: Discipline = Discipline.DASHBOARD,
) -> None:
    """A running trial has one open segment; a trial that is not running has none."""
    open_by_trial = {s.trial_id: s for s in store.segments.list_open()}
    changed = []
    for trial in trials:
        segment = open_by_trial.get(trial.id)
        if trial.timer_started_at is None and segment is not None:
            changed.append(close_segment(segment, now))
        elif trial.timer_started_at is not None and segment is None:
            changed.append(open_segment(str(uuid.uuid4()), trial.id, discipline, now))
    if changed:
        store.segments.save(changed, now)
