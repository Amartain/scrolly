"""Whether the focus room has a run of its own under way. Pure, no IO.

A run goes on after the user steps out (owner, 2026-10-23): coming back finds it where it is, and
the dashboard shows its clock. Incense has no run of its own; the trial's timer is all there is.
"""

from collections.abc import Iterable

from scrolly.domain.cycles import CyclesRun, Phase
from scrolly.domain.flow import FlowBank, FlowPhase
from scrolly.domain.segments import Discipline


def run_under_way(discipline: Discipline, run: CyclesRun, bank: FlowBank) -> bool:
    """Cycles between the first Start and the end of the last cycle, or Flow once started.
    Paused counts: the run is still there to come back to."""
    if discipline is Discipline.CYCLES:
        return run.phase in (Phase.FOCUS, Phase.BREAK, Phase.WAITING)
    if discipline is Discipline.FLOW:
        return bank.phase is not FlowPhase.IDLE
    return False


def focus_began_in_room(running: Iterable[Discipline], under_way: bool) -> bool:
    """A focus started in Seclusion still goes on: the room's run, or a running timer of one of its
    disciplines (the parallel trial too). A timer started on the dashboard does not count until the
    room takes it over. Coming back to such a focus is not shown with the full animation (owner,
    2026-10-23)."""
    return under_way or any(d is not Discipline.DASHBOARD for d in running)
