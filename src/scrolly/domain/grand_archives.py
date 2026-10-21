"""The Grand Archives: past days, newest first, with what became of each trial. Pure, no IO.

Not `archive.py`: that is Backup Scroll, the whole database as tables.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date

from scrolly.domain.models import Trial, TrialState

SENT_BACK = frozenset({TrialState.POSTPONED, TrialState.RETURNED})
SETTLED = frozenset({TrialState.DONE, TrialState.LOST}) | SENT_BACK


@dataclass(frozen=True)
class ArchiveDay:
    day: date
    conquered: list[Trial]
    lost: list[Trial]
    sent_back: list[Trial]
    # Days with nothing settled between this one and the next newer card; 0 for the newest.
    rest_before: int
    trials: list[Trial]  # everything settled that day, for its Essence line


def _when(trial: Trial) -> float:
    return trial.completed_at.timestamp() if trial.completed_at else float("inf")


def archive_days(trials: Sequence[Trial], today: date) -> list[ArchiveDay]:
    """The days before `today` with something settled, newest first. Open trials are left out."""
    by_day: dict[date, list[Trial]] = {}
    for trial in trials:
        if trial.logical_day < today and trial.state in SETTLED:
            by_day.setdefault(trial.logical_day, []).append(trial)
    days = sorted(by_day, reverse=True)
    return [
        ArchiveDay(
            day=day,
            conquered=sorted(
                (t for t in by_day[day] if t.state is TrialState.DONE),
                key=_when,
            ),
            lost=[t for t in by_day[day] if t.state is TrialState.LOST],
            sent_back=[t for t in by_day[day] if t.state in SENT_BACK],
            rest_before=0 if index == 0 else (days[index - 1] - day).days - 1,
            trials=by_day[day],
        )
        for index, day in enumerate(days)
    ]
