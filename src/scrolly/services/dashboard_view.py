from dataclasses import dataclass
from datetime import datetime

from scrolly.domain.day_budget import light_left
from scrolly.domain.day_flow import immediate_of
from scrolly.domain.essence import EssenceBar, EssenceSummary, essence_bar, essence_summary
from scrolly.domain.logical_day import logical_day
from scrolly.domain.models import Trial, TrialState
from scrolly.domain.stats import heavenly_cycles, lifetime_conquered
from scrolly.domain.sunset import budget_sunset
from scrolly.domain.timer import elapsed_seconds
from scrolly.ports import Store
from scrolly.services.charts_view import Series, build_charts
from scrolly.services.sunset import load_prefs
from scrolly.services.victory import VictoryView, build_victory


@dataclass(frozen=True)
class TimerView:
    """The Immediate Trial's timer at the moment of the view. The browser animates from here."""

    elapsed_s: int
    running: bool
    expected_s: int | None


@dataclass(frozen=True)
class DashboardView:
    immediate: Trial | None
    timer: TimerView | None
    conquered: list[Trial]
    postponed: list[Trial]
    lost: list[Trial]
    essence: EssenceSummary
    essence_bar: EssenceBar
    light_left_min: int | None  # None without a kept sunset, or once it has passed
    victory: VictoryView | None
    lifetime_conquered: int
    heavenly_cycles: int
    charts: list[Series]


def build_dashboard_view(store: Store, now: datetime) -> DashboardView:
    today = logical_day(now)
    trials = store.trials.list_for_day(today)
    immediate = immediate_of(trials)
    expected = None if immediate is None else immediate.essence_expected_min
    essence = essence_summary(trials)
    sunset = budget_sunset(load_prefs(store))
    light = None if sunset is None else light_left(now, sunset)
    return DashboardView(
        immediate=immediate,
        timer=None
        if immediate is None
        else TimerView(
            elapsed_s=elapsed_seconds(immediate, now),
            running=immediate.timer_started_at is not None,
            expected_s=None if expected is None else expected * 60,
        ),
        conquered=sorted(
            (t for t in trials if t.state is TrialState.DONE),
            key=lambda t: t.completed_at or now,
        ),
        postponed=[t for t in trials if t.state is TrialState.POSTPONED],
        lost=[t for t in trials if t.state is TrialState.LOST],
        essence=essence,
        essence_bar=essence_bar(essence, light),
        light_left_min=light,
        victory=build_victory(store.days.get(today), trials, today),
        lifetime_conquered=lifetime_conquered(store.trials.list_all()),
        heavenly_cycles=heavenly_cycles(store.days.list_all()),
        charts=build_charts(store, today),
    )
