from dataclasses import asdict
from typing import Literal

from pydantic import BaseModel

from scrolly.api.schemas.dashboard import ImmediateOut
from scrolly.domain.cycles import CyclesView
from scrolly.domain.cycles import Phase as CyclesPhase
from scrolly.domain.flow import FlowPhase, FlowView
from scrolly.domain.legend import TrialType, type_of
from scrolly.domain.models import Trial
from scrolly.domain.run_clock import BREAK_MAX_MIN, CYCLES_MAX, FOCUS_MAX_MIN, RATIO_MAX
from scrolly.domain.seclusion import IncenseState, IncenseView
from scrolly.domain.segments import Discipline
from scrolly.services.seclusion import SeclusionView


class IncenseOut(BaseModel):
    state: IncenseState
    remaining_s: int
    over_s: int

    @classmethod
    def from_view(cls, view: IncenseView) -> "IncenseOut":
        return cls(state=view.state, remaining_s=view.remaining_s, over_s=view.over_s)


class WaitingOut(BaseModel):
    """A trial that waits in Remaining: enough to choose it in "Switch trials"."""

    id: str
    title: str
    type: TrialType

    @classmethod
    def from_trial(cls, trial: Trial) -> "WaitingOut":
        return cls(id=trial.id, title=trial.title, type=type_of(trial.is_mandate, trial.art_kind))


class CyclesPlanIn(BaseModel):
    focus_min: int
    break_min: int
    cycles: int


class CyclesOut(BaseModel):
    """Harmonious Cycles: the time left in this focus or break, from the run's own clock."""

    phase: CyclesPhase
    cycle: int
    cycles: int
    remaining_s: int
    total_s: int
    running: bool

    @classmethod
    def from_view(cls, view: CyclesView) -> "CyclesOut":
        return cls(**asdict(view))


class FlowOut(BaseModel):
    """River Flow: focused time, the rest banked from it, and a break counting the bank down."""

    phase: FlowPhase
    work: int
    rest: int
    focus_s: int
    banked_s: int
    break_left_s: int
    break_total_s: int
    can_break: bool
    break_in_s: int | None
    running: bool

    @classmethod
    def from_view(cls, view: FlowView) -> "FlowOut":
        return cls(**asdict(view))


class LimitsOut(BaseModel):
    """The most the dials may hold. The rules are Python's; the screen only draws the dials."""

    focus_max_min: int
    break_max_min: int
    cycles_max: int
    ratio_max: int

    @classmethod
    def build(cls) -> "LimitsOut":
        return cls(
            focus_max_min=FOCUS_MAX_MIN,
            break_max_min=BREAK_MAX_MIN,
            cycles_max=CYCLES_MAX,
            ratio_max=RATIO_MAX,
        )


class SeclusionOut(BaseModel):
    active: bool
    discipline: Discipline
    trial: ImmediateOut | None
    note: str
    ring_elapsed_s: int
    incense: IncenseOut | None
    gong_in_s: int | None
    plan: CyclesPlanIn
    limits: LimitsOut
    cycles: CyclesOut | None
    flow: FlowOut | None
    remaining: list[WaitingOut]
    # The trial run beside this one: a trial of its own, with its own timer.
    parallel: ImmediateOut | None = None
    sidebar_hidden: bool = False
    # Seconds Restart and Zero out would take off the trial now, so the screen can ask first.
    restart_scrap_s: int = 0
    zero_scrap_s: int = 0
    # A Cycles run or Flow bank goes on, also after stepping out: the dashboard shows its clock.
    run_under_way: bool = False
    # The cultivator meditates on the peak (domain/cultivator.py).
    on_peak: bool = False

    @classmethod
    def from_view(cls, view: SeclusionView) -> "SeclusionOut":
        trial = None
        if view.trial is not None and view.timer is not None:
            trial = ImmediateOut.from_trial(view.trial, view.timer)
        return cls(
            active=view.active,
            discipline=view.discipline,
            trial=trial,
            note="" if view.trial is None else view.trial.note,
            ring_elapsed_s=view.ring_elapsed_s,
            incense=None if view.incense is None else IncenseOut.from_view(view.incense),
            gong_in_s=view.gong_in_s,
            plan=CyclesPlanIn(**asdict(view.plan)),
            limits=LimitsOut.build(),
            cycles=None if view.cycles is None else CyclesOut.from_view(view.cycles),
            flow=None if view.flow is None else FlowOut.from_view(view.flow),
            remaining=[WaitingOut.from_trial(t) for t in view.remaining],
            parallel=None
            if view.parallel is None
            else ImmediateOut.from_trial(view.parallel.trial, view.parallel.timer),
            sidebar_hidden=view.sidebar_hidden,
            restart_scrap_s=view.restart_scrap_s,
            zero_scrap_s=view.zero_scrap_s,
            run_under_way=view.run_under_way,
            on_peak=view.on_peak,
        )


class DisciplineIn(BaseModel):
    discipline: Discipline


class RatioIn(BaseModel):
    work: int
    rest: int


class SidebarHiddenIn(BaseModel):
    hidden: bool


class FinishIn(BaseModel):
    how: Literal["conquered", "abandoned", "postponed"]
    trial_id: str
