"""The Cycles run and the Flow bank of the focus room, and how they move the trial's timer.

Cycles keeps its own clock: a trial can be conquered and the next one carry on inside the same
cycle. Flow banks rest only while a trial is being worked on.
"""

from dataclasses import replace
from datetime import datetime

from scrolly.domain import cycles, flow
from scrolly.domain.cycles import CyclesPlan, CyclesRun, Phase
from scrolly.domain.day_flow import TrialError
from scrolly.domain.flow import FlowBank, FlowPhase
from scrolly.domain.run_clock import RunError
from scrolly.domain.segments import Discipline
from scrolly.ports import Clock, Store
from scrolly.services.seclusion_prefs import load_plan, load_ratio, save_plan, save_ratio
from scrolly.services.seclusion_state import (
    SeclusionState,
    immediate_trial,
    read_state,
    write_state,
)
from scrolly.services.today import TodayService


class RunControl:
    """Start, pause, break and reset the run of the tab that is open."""

    def __init__(self, store: Store, clock: Clock, today: TodayService) -> None:
        self._store = store
        self._clock = clock
        self._today = today

    @property
    def _now(self) -> datetime:
        return self._clock.now()

    def _put(self, state: SeclusionState) -> None:
        write_state(self._store, state, self._now)

    def _pause_trial(self, at: datetime | None = None) -> None:
        trial = immediate_trial(self._store, self._now)
        if trial is not None and trial.timer_started_at is not None:
            self._today.pause_timer(trial.id, at)

    def _start_trial(self, discipline: Discipline) -> None:
        trial = immediate_trial(self._store, self._now)
        if trial is None:
            raise TrialError("There is no trial to focus on")
        self._today.start_timer(trial.id, discipline)

    def _fresh_bank(self) -> FlowBank:
        return FlowBank(*load_ratio(self._store))

    def settle(self) -> SeclusionState:
        """Cross the boundaries that passed unseen, and stop the trial where its focus ended."""
        state = read_state(self._store)
        if state.discipline is Discipline.CYCLES:
            plan = load_plan(self._store)
            run, focus_ended_at = cycles.settle_cycles(state.cycles, plan, self._now)
            if run != state.cycles:
                state = replace(state, cycles=run)
                self._put(state)
            if focus_ended_at is not None:
                self._pause_trial(at=focus_ended_at)
        elif state.discipline is Discipline.FLOW:
            bank, _ = flow.settle_flow(state.flow, self._now)
            if bank != state.flow:
                state = replace(state, flow=bank)
                self._put(state)
        return state

    def start(self, plan: CyclesPlan | None = None) -> None:
        """Start the next focus, or carry on one that is paused (also after a conquest)."""
        state, now = self.settle(), self._now
        if state.discipline is Discipline.CYCLES:
            run = state.cycles
            if run.phase is Phase.BREAK:
                self._put(replace(state, cycles=cycles.resume_run(run, now)))
                return
            started = cycles.start_focus(run, now)
            if run.phase is Phase.IDLE and plan is not None:
                save_plan(self._store, plan, now)
            self._start_trial(Discipline.CYCLES)
            self._put(replace(state, cycles=started))
        elif state.discipline is Discipline.FLOW:
            bank = flow.start_flow(state.flow, now)
            self._start_trial(Discipline.FLOW)
            self._put(replace(state, flow=bank))

    def pause(self) -> None:
        state, now = self.settle(), self._now
        if state.discipline is Discipline.CYCLES:
            run = cycles.pause_run(state.cycles, load_plan(self._store), now)
            self._put(replace(state, cycles=run))
        elif state.discipline is Discipline.FLOW:
            self._put(replace(state, flow=flow.pause_flow(state.flow, now)))
        self._pause_trial()

    def take_break(self) -> None:
        state, now = self.settle(), self._now
        if state.discipline is Discipline.CYCLES:
            self._put(replace(state, cycles=cycles.take_break_now(state.cycles, now)))
        else:
            self._put(replace(state, flow=flow.start_break(state.flow, now)))
        self._pause_trial()

    def end_break(self) -> None:
        state, now = self.settle(), self._now
        if state.discipline is Discipline.CYCLES:
            run = cycles.skip_break(state.cycles, load_plan(self._store))
            self._put(replace(state, cycles=run))
        else:
            self._put(replace(state, flow=flow.end_break(state.flow, now)))

    def reset(self) -> None:
        """Start over: the dial again (Cycles) or an empty bank (Flow). Logged time stays."""
        state = self.settle()
        self._pause_trial()
        self._put(replace(state, cycles=CyclesRun(), flow=self._fresh_bank()))

    def switch(self, discipline: Discipline) -> None:
        """Another tab. The segment closes (its time stays on the trial); a fresh run waits."""
        if discipline is Discipline.DASHBOARD:
            raise RunError("That is not a tab of the room")
        state = self.settle()
        self._pause_trial()
        fresh = replace(state, discipline=discipline, cycles=CyclesRun(), flow=self._fresh_bank())
        self._put(fresh)

    def set_ratio(self, work: int, rest: int) -> None:
        state = self.settle()
        bank = flow.set_ratio(state.flow, work, rest)
        save_ratio(self._store, work, rest, self._now)
        self._put(replace(state, flow=bank))

    def before_finish(self) -> None:
        """A trial is about to end. Flow stops banking; Cycles carries on with its own clock."""
        state = self.settle()
        if state.discipline is Discipline.FLOW and state.flow.phase is FlowPhase.FOCUS:
            self._put(replace(state, flow=flow.pause_flow(state.flow, self._now)))
