from pydantic import BaseModel

from scrolly.domain.day_budget import DayBudget
from scrolly.domain.duration import format_duration
from scrolly.domain.qi import LINEAR_SPAN
from scrolly.services.golden_core import QiView


def _pct(part: int, whole: int) -> int:
    return 0 if whole <= 0 else min(100, round(100 * part / whole))


class BudgetOut(BaseModel):
    """The Day Summary. Bar widths are shares of its span: the light left, or the plan if larger."""

    trial_count: int
    planned_text: str
    light_text: str | None
    beyond_text: str | None
    unestimated_count: int
    mandate_pct: int
    mortal_pct: int
    light_pct: int

    @classmethod
    def from_budget(cls, budget: DayBudget) -> "BudgetOut":
        light = budget.light_min
        span = max(light or 0, budget.planned_min)
        return cls(
            trial_count=budget.trial_count,
            planned_text=format_duration(budget.planned_min),
            light_text=None if light is None else format_duration(light),
            beyond_text=format_duration(budget.beyond_light_min)
            if budget.beyond_light_min
            else None,
            unestimated_count=budget.unestimated_count,
            mandate_pct=_pct(budget.mandate_min, span),
            mortal_pct=_pct(budget.mortal_min, span),
            light_pct=0 if light is None else _pct(light, span),
        )


class QiOut(BaseModel):
    """The Golden Core. Gauge shares are of the redline, the top of today's gauge.

    The zones are calm (up to the start), surge (the next stretch) and redline (the rest).
    `*_end_pct` are where the first two end; `fill_*_pct` are how much of each zone is filled.
    """

    enabled: bool
    invited: bool
    planned: int
    start: int
    low: int
    high: int
    surge_end: int
    redline: int
    tomorrow_start: int
    calm_end_pct: int
    surge_end_pct: int
    fill_calm_pct: int
    fill_surge_pct: int
    fill_redline_pct: int

    @classmethod
    def from_view(cls, view: QiView) -> "QiOut":
        surge_end = view.start + LINEAR_SPAN
        in_calm = min(view.planned, view.start)
        in_surge = max(0, min(view.planned, surge_end) - view.start)
        in_redline = max(0, min(view.planned, view.redline) - surge_end)
        return cls(
            enabled=view.enabled,
            invited=view.invited,
            planned=view.planned,
            start=view.start,
            low=view.low,
            high=view.high,
            surge_end=surge_end,
            redline=view.redline,
            tomorrow_start=view.tomorrow_start,
            calm_end_pct=_pct(view.start, view.redline),
            surge_end_pct=_pct(surge_end, view.redline),
            fill_calm_pct=_pct(in_calm, view.redline),
            fill_surge_pct=_pct(in_surge, view.redline),
            fill_redline_pct=_pct(in_redline, view.redline),
        )
