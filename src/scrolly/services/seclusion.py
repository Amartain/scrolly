from dataclasses import dataclass, replace
from datetime import datetime
from typing import Literal

from scrolly.domain.cycles import CyclesPlan, CyclesView, cycles_view
from scrolly.domain.day_flow import TrialError, immediate_of
from scrolly.domain.flow import FlowView, flow_view
from scrolly.domain.logical_day import logical_day
from scrolly.domain.models import Trial, TrialState
from scrolly.domain.seclusion import IncenseView, incense_view, ring_elapsed, seconds_to_gong
from scrolly.domain.segments import Discipline
from scrolly.domain.timer import elapsed_seconds
from scrolly.ports import Clock, Store
from scrolly.services.dashboard_view import TimerView
from scrolly.services.day import run_rollover
from scrolly.services.scraps import ScrapService
from scrolly.services.seclusion_correct import TimerCorrection, scrap_preview
from scrolly.services.seclusion_parallel import ParallelControl, ParallelView
from scrolly.services.seclusion_prefs import load_plan, load_sidebar_hidden
from scrolly.services.seclusion_runs import RunControl
from scrolly.services.seclusion_state import read_state, working_day, write_state
from scrolly.services.today import TodayService


@dataclass(frozen=True)
class SeclusionView:
    active: bool
    discipline: Discipline
    trial: Trial | None
    timer: TimerView | None
    ring_elapsed_s: int
    incense: IncenseView | None  # None until the trial has an estimate
    gong_in_s: int | None  # only in Incense, while the timer runs and there is an estimate
    plan: CyclesPlan  # what the dial last held
    cycles: CyclesView | None  # only on the Cycles tab
    flow: FlowView | None  # only on the Flow tab
    remaining: list[Trial]
    parallel: ParallelView | None = None  # the trial run beside this one
    sidebar_hidden: bool = False  # the Parallel sidebar is folded to a strip
    restart_scrap_s: int = 0  # what Restart would take off the trial now
    zero_scrap_s: int = 0  # what Zero out would take off the trial now


class SeclusionService:
    """The focus room: one trial, its timer, nothing else. Time is paced, never punished."""

    def __init__(self, store: Store, clock: Clock) -> None:
        self._store = store
        self._clock = clock
        self._today = TodayService(store, clock)
        self._runs = RunControl(store, clock, self._today)
        self._scraps = ScrapService(store, clock)
        self.parallel = ParallelControl(store, clock, self._today, self._scraps)
        self.timer = TimerCorrection(store, clock, self._today, self._runs)

    @property
    def _now(self) -> datetime:
        return self._clock.now()

    def _trials(self) -> list[Trial]:
        return self._store.trials.list_for_day(working_day(self._store, self._now))

    def _immediate(self) -> Trial:
        trial = immediate_of(self._trials())
        if trial is None:
            raise TrialError("There is no trial to focus on")
        return trial

    def enter(self) -> None:
        state = read_state(self._store)
        if state.active:
            return
        trial = self._immediate()
        day = logical_day(self._now)
        write_state(self._store, replace(state, active=True, day=day), self._now)
        self._scraps.open()
        if trial.timer_started_at is not None:
            self._runs.switch(Discipline.INCENSE)  # started on the dashboard: it carries on here
            self._today.start_timer(trial.id, Discipline.INCENSE)
            self._scraps.note_trial(trial.id)

    def leave(self) -> None:
        """Stepping out pauses the trial and the run. A scroll held past 04:00 now rolls over."""
        state = read_state(self._store)
        if not state.active:
            return
        self._runs.pause()
        self.parallel.pause()
        write_state(self._store, replace(read_state(self._store), active=False), self._now)
        self._scraps.close()
        run_rollover(self._store, logical_day(self._now), self._now)

    def switch(self, discipline: Discipline) -> None:
        self._runs.switch(discipline)

    def start(self, plan: CyclesPlan | None = None) -> None:
        if read_state(self._store).discipline is Discipline.INCENSE:
            self._today.start_timer(self._immediate().id, Discipline.INCENSE)
        else:
            self._runs.start(plan)
        trial = immediate_of(self._trials())
        if trial is not None and trial.timer_started_at is not None:  # a break starts no trial
            self._scraps.note_trial(trial.id)

    def pause(self) -> None:
        self._runs.pause()

    def take_break(self) -> None:
        self._runs.take_break()

    def end_break(self) -> None:
        self._runs.end_break()

    def set_ratio(self, work: int, rest: int) -> None:
        self._runs.set_ratio(work, rest)

    def finish(self, how: Literal["conquered", "abandoned", "postponed"], trial_id: str) -> None:
        """End the trial at hand. Cycles carries on with its own clock; Flow stops banking."""
        self._runs.before_finish()
        end = {
            "conquered": self._today.conquer,
            "abandoned": self._today.abandon,
            "postponed": self._today.postpone,
        }[how]
        end(trial_id)

    def view(self) -> SeclusionView:
        hidden = load_sidebar_hidden(self._store)
        return replace(self._room_view(), parallel=self.parallel.view(), sidebar_hidden=hidden)

    def _room_view(self) -> SeclusionView:
        state = self._runs.settle()
        now = self._now
        trials = self._trials()
        trial = immediate_of(trials)
        plan = load_plan(self._store)
        # The trial run beside is not offered: one trial is never both main and parallel.
        beside = state.parallel_id
        waiting = (t for t in trials if t.state is TrialState.REMAINING and t.id != beside)
        remaining = sorted(waiting, key=lambda t: t.position)
        cycles = (
            cycles_view(state.cycles, plan, now) if state.discipline is Discipline.CYCLES else None
        )
        flow = flow_view(state.flow, now) if state.discipline is Discipline.FLOW else None
        if trial is None:
            return SeclusionView(
                state.active,
                state.discipline,
                None,
                None,
                0,
                None,
                None,
                plan,
                cycles,
                flow,
                remaining,
            )
        elapsed = elapsed_seconds(trial, now)
        running = trial.timer_started_at is not None
        expected = None if trial.essence_expected_min is None else trial.essence_expected_min * 60
        ring = ring_elapsed(elapsed, state.baselines.get(trial.id, 0))
        incense = state.discipline is Discipline.INCENSE
        restart_scrap, zero_scrap = scrap_preview(state, trial, now)
        return SeclusionView(
            active=state.active,
            discipline=state.discipline,
            trial=trial,
            timer=TimerView(elapsed, running, expected),
            ring_elapsed_s=ring,
            incense=None if expected is None else incense_view(ring, expected),
            gong_in_s=seconds_to_gong(ring, expected) if incense and running and expected else None,
            plan=plan,
            cycles=cycles,
            flow=flow,
            remaining=remaining,
            restart_scrap_s=restart_scrap,
            zero_scrap_s=zero_scrap,
        )
