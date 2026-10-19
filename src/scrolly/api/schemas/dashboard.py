from pydantic import BaseModel

from scrolly.domain.duration import format_duration
from scrolly.domain.essence import EssenceSummary
from scrolly.domain.legend import TrialType, type_of
from scrolly.domain.models import OriginType, Trial
from scrolly.services.dashboard_view import DashboardView, TimerView


def _minutes(minutes: int | None) -> str:
    return "" if minutes is None else format_duration(minutes)


def _qi(qi: int | None) -> str:
    return "" if qi is None else str(qi)


class TimerOut(BaseModel):
    """The timer as of this view: the browser animates the seconds until the next one."""

    elapsed_s: int
    running: bool
    expected_s: int | None

    @classmethod
    def from_view(cls, timer: TimerView) -> "TimerOut":
        return cls(elapsed_s=timer.elapsed_s, running=timer.running, expected_s=timer.expected_s)


class ImmediateOut(BaseModel):
    id: str
    title: str
    is_mandate: bool
    origin_type: OriginType
    type: TrialType
    expected_text: str
    qi_text: str
    timer: TimerOut

    @classmethod
    def from_trial(cls, trial: Trial, timer: TimerView) -> "ImmediateOut":
        return cls(
            id=trial.id,
            title=trial.title,
            is_mandate=trial.is_mandate,
            origin_type=trial.origin_type,
            type=type_of(trial.is_mandate, trial.origin_type),
            expected_text=_minutes(trial.essence_expected_min),
            qi_text=_qi(trial.qi_expected),
            timer=TimerOut.from_view(timer),
        )


class ConqueredOut(BaseModel):
    id: str
    title: str
    is_mandate: bool
    origin_type: OriginType
    type: TrialType
    actual_text: str
    qi_text: str

    @classmethod
    def from_trial(cls, trial: Trial) -> "ConqueredOut":
        return cls(
            id=trial.id,
            title=trial.title,
            is_mandate=trial.is_mandate,
            origin_type=trial.origin_type,
            type=type_of(trial.is_mandate, trial.origin_type),
            actual_text=_minutes(trial.essence_actual_min),
            qi_text=_qi(trial.qi_actual if trial.qi_actual is not None else trial.qi_expected),
        )


class EssenceOut(BaseModel):
    actual_text: str
    expected_text: str
    remaining_text: str
    meter_pct: int

    @classmethod
    def from_summary(cls, summary: EssenceSummary) -> "EssenceOut":
        return cls(
            actual_text=format_duration(summary.actual_min),
            expected_text=format_duration(summary.expected_min),
            remaining_text=format_duration(summary.remaining_min),
            meter_pct=summary.meter_pct,
        )


class LetGoOut(BaseModel):
    """A trial sent to the Horizon today (`postponed`) or let go (`lost`)."""

    id: str
    title: str
    type: TrialType

    @classmethod
    def from_trial(cls, trial: Trial) -> "LetGoOut":
        return cls(
            id=trial.id, title=trial.title, type=type_of(trial.is_mandate, trial.origin_type)
        )


class DashboardOut(BaseModel):
    immediate: ImmediateOut | None
    conquered: list[ConqueredOut]
    postponed: list[LetGoOut]
    lost: list[LetGoOut]
    essence: EssenceOut
    victory: bool
    lifetime_conquered: int
    heavenly_cycles: int

    @classmethod
    def from_data(cls, data: DashboardView) -> "DashboardOut":
        immediate = None
        if data.immediate is not None and data.timer is not None:
            immediate = ImmediateOut.from_trial(data.immediate, data.timer)
        return cls(
            immediate=immediate,
            conquered=[ConqueredOut.from_trial(t) for t in data.conquered],
            postponed=[LetGoOut.from_trial(t) for t in data.postponed],
            lost=[LetGoOut.from_trial(t) for t in data.lost],
            essence=EssenceOut.from_summary(data.essence),
            victory=data.victory,
            lifetime_conquered=data.lifetime_conquered,
            heavenly_cycles=data.heavenly_cycles,
        )


class ScribeIn(BaseModel):
    title: str
    estimate: str = ""
    qi: str = ""


class TrialPatchIn(BaseModel):
    """Only the fields that are sent change. A conquered trial is read-only."""

    title: str | None = None
    is_mandate: bool | None = None
    estimate: str | None = None
    qi: str | None = None
