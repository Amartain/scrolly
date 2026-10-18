from collections.abc import Callable, Sequence
from contextlib import AbstractContextManager
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Protocol

from scrolly.domain.models import Art, Day, HorizonItem, Trial


class Clock(Protocol):
    def now(self) -> datetime: ...


class SettingsRepository(Protocol):
    def get(self, key: str) -> dict[str, Any] | None: ...

    def set(self, key: str, value: dict[str, Any], now: datetime) -> None: ...


class TrialRepository(Protocol):
    def list_all(self) -> list[Trial]: ...

    def list_open_before(self, day: date) -> list[Trial]: ...

    def save(self, trials: Sequence[Trial], now: datetime) -> None: ...


class HorizonRepository(Protocol):
    def list_all(self) -> list[HorizonItem]: ...

    def replace_all(self, items: Sequence[HorizonItem], now: datetime) -> None: ...


class ArtRepository(Protocol):
    def list_all(self) -> list[Art]: ...

    def save(self, arts: Sequence[Art], now: datetime) -> None: ...


class DayRepository(Protocol):
    def get(self, day: date) -> Day | None: ...

    def list_all(self) -> list[Day]: ...

    def save(self, day: Day, now: datetime) -> None: ...


@dataclass(frozen=True)
class Store:
    """Everything one request may touch. One store = one transaction."""

    settings: SettingsRepository
    trials: TrialRepository
    horizon: HorizonRepository
    arts: ArtRepository
    days: DayRepository
    commit: Callable[[], None]


StoreFactory = Callable[[], AbstractContextManager[Store]]
