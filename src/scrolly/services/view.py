from dataclasses import dataclass
from datetime import date, datetime

from scrolly.domain.appearance import Appearance, resolve_appearance
from scrolly.domain.logical_day import logical_day
from scrolly.ports import Clock, Store
from scrolly.services.appearance import AppearanceService
from scrolly.services.day import DayService
from scrolly.services.planning_view import PlanningView, build_planning_view


@dataclass(frozen=True)
class ViewData:
    now: datetime
    logical_day: date
    appearance: Appearance
    planning: PlanningView


def build_view(store: Store, clock: Clock) -> ViewData:
    """Everything the frontend renders, already computed."""
    DayService(store, clock).ensure_today()
    now = clock.now()
    prefs = AppearanceService(store, clock).preferences()
    today = logical_day(now)
    return ViewData(
        now=now,
        logical_day=today,
        appearance=resolve_appearance(prefs, now),
        planning=build_planning_view(store, today),
    )
