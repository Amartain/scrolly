from pydantic import BaseModel

from scrolly.domain.day_budget import DayBudget
from scrolly.domain.duration import format_duration
from scrolly.domain.qi import LINEAR_SPAN, QiZone, gauge_fill, qi_zone
from scrolly.services.golden_core import QiView
from scrolly.services.qi_card import QiCardView


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
    has_sunset: bool

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
            has_sunset=budget.has_sunset,
        )


class QiFillOut(BaseModel):
    """How much of each gauge zone a Qi value fills, as shares of the redline."""

    calm_pct: int
    surge_pct: int
    redline_pct: int

    @classmethod
    def of(cls, value: int, start: int, redline: int) -> "QiFillOut":
        fill = gauge_fill(value, start)
        return cls(
            calm_pct=_pct(fill.calm, redline),
            surge_pct=_pct(fill.surge, redline),
            redline_pct=_pct(fill.redline, redline),
        )


class QiOut(BaseModel):
    """The Golden Core. Gauge shares are of the redline, the top of today's gauge.

    The zones are calm (up to the start), surge (the next stretch) and redline (the rest).
    `*_end_pct` are where the first two end. Planning shows `planned_fill`, the dashboard
    `spent_fill` (conquered Qi only).
    """

    enabled: bool
    invited: bool
    planned: int
    spent: int
    start: int
    low: int
    high: int
    surge_end: int
    redline: int
    tomorrow_start: int
    calm_end_pct: int
    surge_end_pct: int
    planned_fill: QiFillOut
    spent_fill: QiFillOut
    planned_zone: QiZone
    spent_zone: QiZone

    @classmethod
    def from_view(cls, view: QiView) -> "QiOut":
        surge_end = view.start + LINEAR_SPAN
        return cls(
            enabled=view.enabled,
            invited=view.invited,
            planned=view.planned,
            spent=view.spent,
            start=view.start,
            low=view.low,
            high=view.high,
            surge_end=surge_end,
            redline=view.redline,
            tomorrow_start=view.tomorrow_start,
            calm_end_pct=_pct(view.start, view.redline),
            surge_end_pct=_pct(surge_end, view.redline),
            planned_fill=QiFillOut.of(view.planned, view.start, view.redline),
            spent_fill=QiFillOut.of(view.spent, view.start, view.redline),
            planned_zone=qi_zone(view.planned, view.start),
            spent_zone=qi_zone(view.spent, view.start),
        )


class QiChoicesOut(BaseModel):
    lighter: int
    foreseen: int
    heavier: int


class QiCardOut(BaseModel):
    """The card after a conquest: its three choices, and the day's Qi if the asked answer is kept,
    on the dashboard bar's scale (shares of the redline)."""

    choices: QiChoicesOut
    spent: int
    start: int
    zone: QiZone
    fill_pct: int
    calm_end_pct: int
    surge_end_pct: int

    @classmethod
    def from_view(cls, view: QiCardView) -> "QiCardOut":
        return cls(
            choices=QiChoicesOut(**vars(view.choices)),
            spent=view.spent,
            start=view.start,
            zone=qi_zone(view.spent, view.start),
            fill_pct=_pct(view.spent, view.redline),
            calm_end_pct=_pct(view.start, view.redline),
            surge_end_pct=_pct(view.start + LINEAR_SPAN, view.redline),
        )
