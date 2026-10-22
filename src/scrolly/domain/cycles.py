"""Harmonious Cycles: focus, then a break, for as many cycles as the user sets. Pure, no IO.

The run has its own clock, apart from any trial's timer. Only the first focus waits for Start; then
it runs straight through: focus, break, focus, break, for every cycle, each phase beginning when the
last one ends (owner, 2026-10-22). Every boundary is found by timestamp, so a closed tab or a
sleeping machine loses nothing.
"""

from dataclasses import dataclass, field, replace
from datetime import datetime
from enum import StrEnum

from scrolly.domain.run_clock import (
    BREAK_MAX_MIN,
    CYCLES_MAX,
    FOCUS_MAX_MIN,
    RunClock,
    RunError,
    check_range,
    reached_at,
    run_elapsed,
    run_pause,
    run_start,
)


class Phase(StrEnum):
    IDLE = "idle"  # the dial: nothing set going yet
    FOCUS = "focus"
    BREAK = "break"
    WAITING = "waiting"  # kept for runs saved before 2026-10-22: the next focus waits for Start
    DONE = "done"  # every cycle is finished


@dataclass(frozen=True)
class CyclesPlan:
    focus_min: int = 45
    break_min: int = 15
    cycles: int = 3

    @property
    def focus_s(self) -> int:
        return self.focus_min * 60

    @property
    def break_s(self) -> int:
        return self.break_min * 60


def make_plan(focus_min: int, break_min: int, cycles: int) -> CyclesPlan:
    return CyclesPlan(
        check_range(focus_min, 1, FOCUS_MAX_MIN, "Focus"),
        check_range(break_min, 1, BREAK_MAX_MIN, "The break"),
        check_range(cycles, 1, CYCLES_MAX, "The number of cycles"),
    )


@dataclass(frozen=True)
class CyclesRun:
    phase: Phase = Phase.IDLE
    cycle: int = 1
    clock: RunClock = field(default_factory=RunClock)  # the clock of the current focus or break


@dataclass(frozen=True)
class CyclesView:
    phase: Phase
    cycle: int
    cycles: int
    remaining_s: int
    total_s: int
    running: bool


def start_focus(run: CyclesRun, now: datetime) -> CyclesRun:
    """Start (or, from the dial, begin) a focus. Only a run that is not mid-way can start one."""
    if run.phase in (Phase.BREAK, Phase.DONE):
        raise RunError("A cycle is already under way")
    if run.phase is Phase.FOCUS:
        return replace(run, clock=run_start(run.clock, now))
    return CyclesRun(Phase.FOCUS, run.cycle, run_start(RunClock(), now))


def pause_run(run: CyclesRun, plan: CyclesPlan, now: datetime) -> CyclesRun:
    settled, _ = settle_cycles(run, plan, now)
    return replace(settled, clock=run_pause(settled.clock, now))


def resume_run(run: CyclesRun, now: datetime) -> CyclesRun:
    if run.phase not in (Phase.FOCUS, Phase.BREAK):
        return run
    return replace(run, clock=run_start(run.clock, now))


@dataclass(frozen=True)
class Boundary:
    """A focus that began or ended by itself, and when: the trial's timer follows it."""

    at: datetime
    focus_begins: bool


def _after_focus(run: CyclesRun, at: datetime) -> CyclesRun:
    """Every focus is followed by its break, the last one too."""
    return CyclesRun(Phase.BREAK, run.cycle, run_start(RunClock(), at))


def _after_break(run: CyclesRun, plan: CyclesPlan, at: datetime) -> CyclesRun:
    """The next cycle's focus begins at once; after the last cycle's break the run is done."""
    if run.cycle >= plan.cycles:
        return CyclesRun(Phase.DONE, run.cycle)
    return CyclesRun(Phase.FOCUS, run.cycle + 1, run_start(RunClock(), at))


def settle_cycles(
    run: CyclesRun, plan: CyclesPlan, now: datetime
) -> tuple[CyclesRun, list[Boundary]]:
    """Cross every boundary that has passed, in order. Returns the run and each focus that ended
    or began on the way, so the trial's timer can follow."""
    crossed: list[Boundary] = []
    while True:
        if run.phase is Phase.FOCUS and (ended := reached_at(run.clock, plan.focus_s, now)):
            run = _after_focus(run, ended)
            crossed.append(Boundary(ended, focus_begins=False))
        elif run.phase is Phase.BREAK and (ended := reached_at(run.clock, plan.break_s, now)):
            run = _after_break(run, plan, ended)
            if run.phase is Phase.FOCUS:
                crossed.append(Boundary(ended, focus_begins=True))
        else:
            return run, crossed


def take_break_now(run: CyclesRun, now: datetime) -> CyclesRun:
    """End this focus early: the break begins at once, and the cycle counts as done."""
    if run.phase is not Phase.FOCUS:
        raise RunError("There is no focus to rest from")
    return CyclesRun(Phase.BREAK, run.cycle, run_start(RunClock(), now))


def restart_run(now: datetime) -> CyclesRun:
    """Begin again from the first cycle: its focus runs at once."""
    return CyclesRun(Phase.FOCUS, 1, run_start(RunClock(), now))


def zero_phase(run: CyclesRun, now: datetime) -> CyclesRun:
    """The focus or break under way starts over from 0, in the same cycle. Running stays running."""
    if run.phase not in (Phase.FOCUS, Phase.BREAK):
        raise RunError("There is nothing to zero out yet")
    clock = RunClock(now) if run.clock.running else RunClock()
    return replace(run, clock=clock)


def skip_break(run: CyclesRun, plan: CyclesPlan, now: datetime) -> CyclesRun:
    """End the break early: the next focus begins now (after the last cycle, the run is done)."""
    if run.phase is not Phase.BREAK:
        raise RunError("There is no break to skip")
    return _after_break(run, plan, now)


def cycles_view(run: CyclesRun, plan: CyclesPlan, now: datetime) -> CyclesView:
    """What the ring shows: the time left in this phase, counted from the run's own clock."""
    total = {Phase.FOCUS: plan.focus_s, Phase.BREAK: plan.break_s}.get(run.phase, plan.focus_s)
    left = total
    if run.phase in (Phase.FOCUS, Phase.BREAK):
        left = max(0, total - run_elapsed(run.clock, now))
    return CyclesView(run.phase, run.cycle, plan.cycles, left, total, run.clock.running)
