from collections.abc import Callable
from contextlib import AbstractContextManager
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol


class Clock(Protocol):
    def now(self) -> datetime: ...


class SettingsRepository(Protocol):
    def get(self, key: str) -> dict[str, Any] | None: ...

    def set(self, key: str, value: dict[str, Any], now: datetime) -> None: ...


@dataclass(frozen=True)
class Store:
    """Everything one request may touch. One store = one transaction."""

    settings: SettingsRepository
    commit: Callable[[], None]


StoreFactory = Callable[[], AbstractContextManager[Store]]
