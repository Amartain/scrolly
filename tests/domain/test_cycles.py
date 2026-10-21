from datetime import UTC, datetime, timedelta

import pytest

from scrolly.domain.cycles import (
    Boundary,
    CyclesPlan,
    CyclesRun,
    Phase,
    cycles_view,
    make_plan,
    pause_run,
    resume_run,
    settle_cycles,
    skip_break,
    start_focus,
    take_break_now,
)
from scrolly.domain.run_clock import RunError

T0 = datetime(2026, 10, 20, 9, 0, tzinfo=UTC)
PLAN = CyclesPlan(focus_min=45, break_min=15, cycles=3)


def at(minutes: float) -> datetime:
    return T0 + timedelta(minutes=minutes)


def test_the_defaults_are_forty_five_and_fifteen() -> None:
    assert (CyclesPlan().focus_min, CyclesPlan().break_min) == (45, 15)


def test_the_cycles_run_straight_through_however_late_we_look() -> None:
    # 45 / 15 for 3 cycles, looked at after two hours: two cycles done, the third focus under way.
    settled, crossed = settle_cycles(start_focus(CyclesRun(), T0), PLAN, at(120))
    assert crossed == [
        Boundary(at(45), focus_begins=False),
        Boundary(at(60), focus_begins=True),
        Boundary(at(105), focus_begins=False),
        Boundary(at(120), focus_begins=True),
    ]
    assert (settled.phase, settled.cycle, settled.clock.running) == (Phase.FOCUS, 3, True)


def test_the_break_begins_by_itself_when_focus_ends() -> None:
    run = start_focus(CyclesRun(), T0)
    settled, crossed = settle_cycles(run, PLAN, at(50))
    assert crossed == [Boundary(at(45), focus_begins=False)]
    assert settled.phase is Phase.BREAK
    assert cycles_view(settled, PLAN, at(50)).remaining_s == 10 * 60


def test_after_a_break_the_next_focus_begins_by_itself() -> None:
    run, _ = settle_cycles(start_focus(CyclesRun(), T0), PLAN, at(61))
    assert (run.phase, run.cycle) == (Phase.FOCUS, 2)
    assert cycles_view(run, PLAN, at(61)).remaining_s == 44 * 60


def test_two_one_minute_cycles_are_focus_break_focus_break_then_done() -> None:
    plan = CyclesPlan(1, 1, 2)
    run = start_focus(CyclesRun(), T0)
    seen = [settle_cycles(run, plan, at(m))[0].phase for m in (0.5, 1.5, 2.5, 3.5, 4.5)]
    assert seen == [Phase.FOCUS, Phase.BREAK, Phase.FOCUS, Phase.BREAK, Phase.DONE]
    assert cycles_view(settle_cycles(run, plan, at(9))[0], plan, at(9)).running is False


def test_pausing_moves_the_end_of_focus_later() -> None:
    run = pause_run(start_focus(CyclesRun(), T0), PLAN, at(40))
    run = resume_run(run, at(100))
    _, crossed = settle_cycles(run, PLAN, at(120))
    assert crossed[0] == Boundary(at(105), focus_begins=False)


def test_take_a_break_now_starts_the_break_at_once() -> None:
    run = take_break_now(start_focus(CyclesRun(), T0), at(10))
    assert run.phase is Phase.BREAK
    assert cycles_view(run, PLAN, at(10)).remaining_s == 15 * 60


def test_a_break_taken_early_on_the_last_cycle_still_ends_in_done() -> None:
    run = CyclesRun(Phase.FOCUS, 3, start_focus(CyclesRun(), T0).clock)
    run = take_break_now(run, at(10))
    assert settle_cycles(run, PLAN, at(30))[0].phase is Phase.DONE


def test_skipping_a_break_begins_the_next_focus_at_once() -> None:
    run, _ = settle_cycles(start_focus(CyclesRun(), T0), PLAN, at(50))
    skipped = skip_break(run, PLAN, at(50))
    assert (skipped.phase, skipped.cycle, skipped.clock.started_at) == (Phase.FOCUS, 2, at(50))


def test_skipping_the_last_break_ends_the_run() -> None:
    run = take_break_now(CyclesRun(Phase.FOCUS, 3, start_focus(CyclesRun(), T0).clock), at(10))
    assert skip_break(run, PLAN, at(11)).phase is Phase.DONE


def test_a_focus_cannot_start_in_the_middle_of_a_break() -> None:
    run, _ = settle_cycles(start_focus(CyclesRun(), T0), PLAN, at(50))
    with pytest.raises(RunError):
        start_focus(run, at(51))


@pytest.mark.parametrize(
    ("focus", "rest", "cycles"), [(0, 15, 3), (121, 15, 3), (45, 61, 3), (45, 15, 13)]
)
def test_settings_outside_their_limits_are_refused(focus: int, rest: int, cycles: int) -> None:
    with pytest.raises(RunError):
        make_plan(focus, rest, cycles)


def test_the_limits_themselves_are_allowed() -> None:
    assert make_plan(120, 60, 12) == CyclesPlan(120, 60, 12)
    assert make_plan(1, 1, 1) == CyclesPlan(1, 1, 1)
