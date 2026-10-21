"""The Grand Archives page: past days as cards, fourteen at a time, newest first."""

from dataclasses import dataclass
from datetime import date, datetime

from scrolly.domain.duration import format_duration
from scrolly.domain.essence import essence_summary
from scrolly.domain.grand_archives import ArchiveDay, archive_days
from scrolly.domain.legend import TrialType, type_of
from scrolly.domain.logical_day import logical_day
from scrolly.domain.models import Trial
from scrolly.ports import Store

PAGE_DAYS = 14


@dataclass(frozen=True)
class ArchiveRow:
    id: str
    title: str
    type: TrialType
    expected_text: str
    actual_text: str
    qi_text: str
    at_text: str  # when it was conquered, "14:05"; blank for the rest


@dataclass(frozen=True)
class ArchiveCard:
    day: date
    day_text: str
    actual_text: str
    expected_text: str
    rest_days: int
    conquered: list[ArchiveRow]
    lost: list[ArchiveRow]
    sent_back: list[ArchiveRow]


@dataclass(frozen=True)
class ArchivePage:
    cards: list[ArchiveCard]
    # Pass this as `before` to read the days older than this page; None when there are none.
    older: date | None


def _minutes(minutes: int | None) -> str:
    return "" if minutes is None else format_duration(minutes)


def _row(trial: Trial, now: datetime) -> ArchiveRow:
    qi = trial.qi_actual if trial.qi_actual is not None else trial.qi_expected
    at = trial.completed_at.astimezone(now.tzinfo) if trial.completed_at else None
    return ArchiveRow(
        id=trial.id,
        title=trial.title,
        type=type_of(trial.is_mandate, trial.art_kind),
        expected_text=_minutes(trial.essence_expected_min),
        actual_text=_minutes(trial.essence_actual_min),
        qi_text="" if qi is None else str(qi),
        at_text="" if at is None else f"{at:%H:%M}",
    )


def _card(entry: ArchiveDay, now: datetime) -> ArchiveCard:
    essence = essence_summary(entry.trials)
    day = entry.day
    return ArchiveCard(
        day=day,
        day_text=f"{day:%A}, {day.day} {day:%B %Y}",
        actual_text=format_duration(essence.actual_min),
        expected_text=format_duration(essence.expected_min),
        rest_days=entry.rest_before,
        conquered=[_row(t, now) for t in entry.conquered],
        lost=[_row(t, now) for t in entry.lost],
        sent_back=[_row(t, now) for t in entry.sent_back],
    )


def build_archives(store: Store, now: datetime, before: date | None = None) -> ArchivePage:
    """Up to fourteen days older than `before` (or than today), newest first."""
    days = archive_days(store.trials.list_all(), logical_day(now))
    if before is not None:
        days = [d for d in days if d.day < before]
    page, rest = days[:PAGE_DAYS], days[PAGE_DAYS:]
    return ArchivePage([_card(d, now) for d in page], page[-1].day if rest else None)
