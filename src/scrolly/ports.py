from collections.abc import Callable, Sequence
from contextlib import AbstractContextManager
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Protocol

from scrolly.domain.archive import Tables
from scrolly.domain.models import Art, Day, HorizonItem, PlanningDraft, Trial
from scrolly.domain.segments import Segment


class Clock(Protocol):
    def now(self) -> datetime: ...


class SettingsRepository(Protocol):
    def get(self, key: str) -> dict[str, Any] | None: ...

    def set(self, key: str, value: dict[str, Any], now: datetime) -> None: ...


class TrialRepository(Protocol):
    def list_all(self) -> list[Trial]: ...

    def list_open_before(self, day: date) -> list[Trial]: ...

    def list_for_day(self, day: date) -> list[Trial]: ...

    def delete(self, ids: Sequence[str]) -> None: ...

    def save(self, trials: Sequence[Trial], now: datetime) -> None: ...


class SegmentRepository(Protocol):
    def list_open(self) -> list[Segment]: ...

    def list_for_trial(self, trial_id: str) -> list[Segment]: ...

    def delete_for_trials(self, trial_ids: Sequence[str]) -> None: ...

    def save(self, segments: Sequence[Segment], now: datetime) -> None: ...


class HorizonRepository(Protocol):
    def list_all(self) -> list[HorizonItem]: ...

    def replace_all(self, items: Sequence[HorizonItem], now: datetime) -> None: ...


class ArtRepository(Protocol):
    def list_all(self) -> list[Art]: ...

    def save(self, arts: Sequence[Art], now: datetime) -> None: ...

    def set_order(self, ids: Sequence[str], now: datetime) -> None: ...

    def delete(self, ids: Sequence[str]) -> None: ...


class DayRepository(Protocol):
    def get(self, day: date) -> Day | None: ...

    def list_all(self) -> list[Day]: ...

    def save(self, day: Day, now: datetime) -> None: ...


class DraftRepository(Protocol):
    def get(self) -> PlanningDraft | None: ...

    def save(self, draft: PlanningDraft, now: datetime) -> None: ...

    def delete(self) -> None: ...


class ArchiveRepository(Protocol):
    def dump(self) -> Tables: ...

    def replace_all(self, tables: Tables) -> int: ...

    def add_missing(self, tables: Tables) -> tuple[int, int]: ...


@dataclass(frozen=True)
class Store:
    """Everything one request may touch. One store = one transaction."""

    settings: SettingsRepository
    trials: TrialRepository
    segments: SegmentRepository
    horizon: HorizonRepository
    arts: ArtRepository
    days: DayRepository
    drafts: DraftRepository
    archive: ArchiveRepository
    commit: Callable[[], None]


StoreFactory = Callable[[], AbstractContextManager[Store]]
