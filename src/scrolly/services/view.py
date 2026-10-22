from dataclasses import dataclass
from datetime import date, datetime

from scrolly.domain.appearance import Appearance, resolve_appearance
from scrolly.domain.day_budget import DayBudget
from scrolly.domain.legend import Legend
from scrolly.domain.logical_day import logical_day
from scrolly.domain.poems import PoemPick
from scrolly.domain.sky import Sky, sky_at
from scrolly.domain.sunset import SunsetPrefs, phase_at
from scrolly.ports import Clock, Store
from scrolly.services.advisor import AdvisorView, build_advisor
from scrolly.services.appearance import AppearanceService
from scrolly.services.dashboard_view import DashboardView, build_dashboard_view
from scrolly.services.day import DayService
from scrolly.services.day_budget import build_budget
from scrolly.services.ghost import GhostView, build_ghost_view
from scrolly.services.golden_core import QiView, build_qi_view
from scrolly.services.legend import load_legend
from scrolly.services.planning_timer import PlanningTimerView, build_planning_timer
from scrolly.services.planning_view import PlanningView, build_planning_view
from scrolly.services.poem import build_poem
from scrolly.services.seclusion_prefs import SoundPrefs, load_sound
from scrolly.services.sunset import load_prefs


@dataclass(frozen=True)
class ViewData:
    now: datetime
    logical_day: date
    appearance: Appearance
    planning: PlanningView
    budget: DayBudget
    qi: QiView
    dashboard: DashboardView
    sunset: SunsetPrefs
    advisor: AdvisorView
    poem: PoemPick | None
    legend: Legend
    planning_timer: PlanningTimerView
    sound: SoundPrefs
    ghost: GhostView | None
    sky: Sky


def build_view(store: Store, clock: Clock) -> ViewData:
    """Everything the frontend renders, already computed."""
    DayService(store, clock).ensure_today()
    now = clock.now()
    prefs = AppearanceService(store, clock).preferences()
    sunset = load_prefs(store)
    today = logical_day(now)
    phase = phase_at(now, sunset, store.days.get(today))
    return ViewData(
        now=now,
        logical_day=today,
        appearance=resolve_appearance(prefs, phase),
        sunset=sunset,
        advisor=build_advisor(store, now, sunset, phase),
        poem=build_poem(store, now, phase),
        legend=load_legend(store),
        planning_timer=build_planning_timer(store, now),
        planning=build_planning_view(store, today),
        budget=build_budget(store, now),
        qi=build_qi_view(store, now),
        dashboard=build_dashboard_view(store, now),
        sound=load_sound(store),
        ghost=build_ghost_view(store),
        sky=sky_at(now, sunset),
    )
