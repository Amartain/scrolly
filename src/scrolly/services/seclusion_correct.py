"""Restart, Zero out and Stop in the focus room: the user's own corrections of a timer.

Restart and Zero out scrap the time since a mark (the screen asks first); Stop keeps it.
"""

from dataclasses import replace
from datetime import datetime

from scrolly.domain.cycles import Phase
from scrolly.domain.day_flow import TrialError, immediate_of
from scrolly.domain.flow import FlowPhase
from scrolly.domain.models import Trial
from scrolly.domain.run_clock import RunError
from scrolly.domain.seclusion import ring_elapsed, since_mark
from scrolly.domain.segments import Discipline
from scrolly.domain.timer import elapsed_seconds
from scrolly.ports import Clock, Store
from scrolly.services.seclusion_runs import RunControl
from scrolly.services.seclusion_state import SeclusionState, read_state, working_day, write_state
from scrolly.services.today import TodayService


def scrap_preview(state: SeclusionState, trial: Trial, now: datetime) -> tuple[int, int]:
    """Seconds that Restart and Zero out would take off the trial at hand right now."""
    logged = elapsed_seconds(trial, now)
    if state.discipline is Discipline.INCENSE:
        return ring_elapsed(logged, state.baselines.get(trial.id, 0)), 0
    in_focus = (state.discipline is Discipline.CYCLES and state.cycles.phase is Phase.FOCUS) or (
        state.discipline is Discipline.FLOW and state.flow.phase is FlowPhase.FOCUS
    )
    restart = since_mark(logged, state.run_marks.get(trial.id))
    zero = since_mark(logged, state.stretch_marks.get(trial.id)) if in_focus else 0
    return restart, zero


class TimerCorrection:
    """The three buttons that set the room's timer back."""

    def __init__(self, store: Store, clock: Clock, today: TodayService, runs: RunControl) -> None:
        self._store = store
        self._clock = clock
        self._today = today
        self._runs = runs

    @property
    def _now(self) -> datetime:
        return self._clock.now()

    def _immediate(self) -> Trial:
        trial = immediate_of(self._store.trials.list_for_day(working_day(self._store, self._now)))
        if trial is None:
            raise TrialError("There is no trial to focus on")
        return trial

    def restart(self) -> None:
        """Begin again from zero, at once. The time on this timer is scrapped."""
        state = read_state(self._store)
        if state.discipline is not Discipline.INCENSE:
            self._runs.restart()
            return
        trial = self._immediate()
        ring = ring_elapsed(elapsed_seconds(trial, self._now), state.baselines.get(trial.id, 0))
        self._today.scrap_time(trial.id, ring)
        baselines = {**state.baselines, trial.id: elapsed_seconds(self._immediate(), self._now)}
        write_state(self._store, replace(state, baselines=baselines), self._now)
        self._today.start_timer(trial.id, Discipline.INCENSE)

    def zero_out(self) -> None:
        """The focus or break under way starts over; a focus's time is scrapped."""
        if read_state(self._store).discipline is Discipline.INCENSE:
            raise RunError("The incense has one stretch: Restart lights it again")
        self._runs.zero_out()

    def stop(self) -> None:
        """End the run and go back to its setup. The time is kept."""
        if read_state(self._store).discipline is Discipline.INCENSE:
            raise RunError("The incense has nothing to stop: pause it instead")
        self._runs.reset()
