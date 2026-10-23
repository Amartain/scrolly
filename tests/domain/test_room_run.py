import pytest

from scrolly.domain.cycles import CyclesRun, Phase
from scrolly.domain.flow import FlowBank, FlowPhase
from scrolly.domain.room_run import focus_began_in_room, run_under_way
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


def test_a_timer_started_on_the_dashboard_is_not_a_focus_of_the_room() -> None:
    assert focus_began_in_room([Discipline.DASHBOARD], under_way=False) is False
    assert focus_began_in_room([], under_way=False) is False


@pytest.mark.parametrize("discipline", [Discipline.INCENSE, Discipline.PARALLEL])
def test_a_timer_of_the_room_is(discipline: Discipline) -> None:
    assert focus_began_in_room([Discipline.DASHBOARD, discipline], under_way=False) is True


def test_a_run_under_way_is_even_in_its_break() -> None:
    assert focus_began_in_room([], under_way=True) is True


def test_incense_has_no_run_of_its_own() -> None:
    busy = CyclesRun(phase=Phase.FOCUS)
    assert run_under_way(Discipline.INCENSE, busy, FlowBank(phase=FlowPhase.FOCUS)) is False
