from collections.abc import Sequence
from dataclasses import dataclass, field, replace
from datetime import date, datetime, time

from scrolly.domain.horizon import has_title, same_title
from scrolly.domain.models import Art, Day, HorizonItem, Trial, TrialState


@dataclass(frozen=True)
class ImportBatch:
    """What an importer found, already in the rebuild's own types."""

    trials: list[Trial] = field(default_factory=list)
    horizon: list[HorizonItem] = field(default_factory=list)
    arts: list[Art] = field(default_factory=list)


@dataclass(frozen=True)
class Existing:
    trials: Sequence[Trial]
    horizon: Sequence[HorizonItem]
    arts: Sequence[Art]
    days: Sequence[Day]


@dataclass(frozen=True)
class ImportSummary:
    trials_added: int
    trials_skipped: int
    horizon_added: int
    horizon_skipped: int
    arts_added: int
    arts_skipped: int

    @property
    def added(self) -> int:
        return self.trials_added + self.horizon_added + self.arts_added

    @property
    def skipped(self) -> int:
        return self.trials_skipped + self.horizon_skipped + self.arts_skipped


@dataclass(frozen=True)
class MergeResult:
    trials: list[Trial]
    horizon: list[HorizonItem]
    arts: list[Art]
    days: list[Day]
    summary: ImportSummary


def _new_trials(existing: Sequence[Trial], incoming: Sequence[Trial]) -> list[Trial]:
    ids = {t.id for t in existing}
    keys = {(t.logical_day, t.title.strip().casefold()) for t in existing}
    added: list[Trial] = []
    for trial in incoming:
        if trial.id in ids or (trial.logical_day, trial.title.strip().casefold()) in keys:
            continue
        ids.add(trial.id)
        added.append(trial)
    return added


def _new_horizon(
    existing: Sequence[HorizonItem], incoming: Sequence[HorizonItem]
) -> list[HorizonItem]:
    items = list(existing)
    for item in incoming:
        if not has_title(items, item.title):
            items.append(item)
    return items


def _new_arts(existing: Sequence[Art], incoming: Sequence[Art]) -> list[Art]:
    arts = list(existing)
    added: list[Art] = []
    for art in incoming:
        if not any(a.kind is art.kind and same_title(a.title, art.title) for a in arts):
            arts.append(art)
            added.append(art)
    return added


def _single_immediate(
    added: Sequence[Trial], existing: Sequence[Trial], today: date
) -> list[Trial]:
    """Today has one Immediate Trial. An imported second one waits at the top of Remaining."""
    taken = any(t.state is TrialState.IMMEDIATE and t.logical_day == today for t in existing)
    todays = [t for t in [*existing, *added] if t.logical_day == today]
    top = min((t.position for t in todays if t.state is TrialState.REMAINING), default=0)
    result: list[Trial] = []
    for trial in added:
        if trial.state is TrialState.IMMEDIATE and trial.logical_day == today:
            if taken:
                top -= 1
                trial = replace(trial, state=TrialState.REMAINING, position=top)
            taken = True
        result.append(trial)
    return result


def _sealed_days(known_days: Sequence[Day], added: Sequence[Trial], now: datetime) -> list[Day]:
    """Every imported day with a trial counts as one sealed day (a Heavenly Cycle)."""
    known = {d.logical_day: d for d in known_days}
    days: list[Day] = []
    for logical in sorted({t.logical_day for t in added}):
        current = known.get(logical) or Day(logical_day=logical)
        if current.first_sealed_at is not None:
            continue
        finished = [t.completed_at for t in added if t.logical_day == logical and t.completed_at]
        noon = datetime.combine(logical, time(12), tzinfo=now.tzinfo)
        days.append(replace(current, first_sealed_at=min(finished, default=noon)))
    return days


def merge_import(existing: Existing, batch: ImportBatch, today: date, now: datetime) -> MergeResult:
    """Add what is missing and skip what is already there, so importing twice changes nothing."""
    trials = _single_immediate(_new_trials(existing.trials, batch.trials), existing.trials, today)
    horizon = _new_horizon(existing.horizon, batch.horizon)
    arts = _new_arts(existing.arts, batch.arts)
    summary = ImportSummary(
        trials_added=len(trials),
        trials_skipped=len(batch.trials) - len(trials),
        horizon_added=len(horizon) - len(existing.horizon),
        horizon_skipped=len(batch.horizon) - (len(horizon) - len(existing.horizon)),
        arts_added=len(arts),
        arts_skipped=len(batch.arts) - len(arts),
    )
    days = _sealed_days(existing.days, trials, now)
    return MergeResult(trials=trials, horizon=horizon, arts=arts, days=days, summary=summary)
