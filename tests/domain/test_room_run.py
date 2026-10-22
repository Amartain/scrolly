import pytest

from scrolly.domain.cycles import CyclesRun, Phase
from scrolly.domain.flow import FlowBank, FlowPhase
from scrolly.domain.room_run import run_under_way
from scrolly.domain.segments import Discipline


@pytest.mark.parametrize(
    ("phase", "under_way"),
    [
        (Phase.IDLE, False),
        (Phase.FOCUS, True),
        (Phase.BREAK, True),
        (Phase.WAITING, True),
        (Phase.DONE, False),
    ],
)
def test_cycles_is_under_way_from_the_first_start_to_the_last_cycle(
    phase: Phase, under_way: bool
) -> None:
    assert run_under_way(Discipline.CYCLES, CyclesRun(phase=phase), FlowBank()) is under_way


@pytest.mark.parametrize(
    ("phase", "under_way"),
    [(FlowPhase.IDLE, False), (FlowPhase.FOCUS, True), (FlowPhase.BREAK, True)],
)
def test_flow_is_under_way_once_started(phase: FlowPhase, under_way: bool) -> None:
    assert run_under_way(Discipline.FLOW, CyclesRun(), FlowBank(phase=phase)) is under_way


def test_incense_has_no_run_of_its_own() -> None:
    busy = CyclesRun(phase=Phase.FOCUS)
    assert run_under_way(Discipline.INCENSE, busy, FlowBank(phase=FlowPhase.FOCUS)) is False
