from dataclasses import dataclass
from datetime import date, datetime

from scrolly.domain.appearance import Appearance, resolve_appearance
from scrolly.domain.logical_day import logical_day
from scrolly.ports import Clock, Store
from scrolly.services.appearance import AppearanceService
from scrolly.services.day import DayService


@dataclass(frozen=True)
class ViewData:
    now: datetime
    logical_day: date
    appearance: Appearance


def build_view(store: Store, clock: Clock) -> ViewData:
    """Everything the frontend renders, already computed."""
    DayService(store, clock).ensure_today()
    now = clock.now()
    prefs = AppearanceService(store, clock).preferences()
    return ViewData(
        now=now, logical_day=logical_day(now), appearance=resolve_appearance(prefs, now)
    )
