from datetime import UTC, datetime, timedelta

import pytest

from scrolly.domain.cycles import (
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


def test_focus_ends_at_the_set_time_however_late_we_look() -> None:
    run = start_focus(CyclesRun(), T0)
    settled, ended = settle_cycles(run, PLAN, at(180))
    assert ended == at(45)
    assert settled.phase is Phase.WAITING and settled.cycle == 2  # the break ran its course too


def test_the_break_begins_by_itself_when_focus_ends() -> None:
    run = start_focus(CyclesRun(), T0)
    settled, ended = settle_cycles(run, PLAN, at(50))
    assert ended == at(45)
    assert settled.phase is Phase.BREAK
    assert cycles_view(settled, PLAN, at(50)).remaining_s == 10 * 60


def test_after_a_break_the_next_focus_waits_for_start() -> None:
    run, _ = settle_cycles(start_focus(CyclesRun(), T0), PLAN, at(61))
    assert run.phase is Phase.WAITING and not run.clock.running
    assert start_focus(run, at(70)).phase is Phase.FOCUS


def test_the_last_cycle_ends_in_done_and_nothing_counts_on() -> None:
    plan = CyclesPlan(1, 1, 1)
    run, ended = settle_cycles(start_focus(CyclesRun(), T0), plan, at(5))
    assert (run.phase, ended) == (Phase.DONE, at(1))
    assert cycles_view(run, plan, at(500)).running is False


def test_pausing_moves_the_end_of_focus_later() -> None:
    run = pause_run(start_focus(CyclesRun(), T0), PLAN, at(40))
    run = resume_run(run, at(100))
    _, ended = settle_cycles(run, PLAN, at(120))
    assert ended == at(105)


def test_take_a_break_now_starts_the_break_at_once() -> None:
    run = take_break_now(start_focus(CyclesRun(), T0), at(10))
    assert run.phase is Phase.BREAK
    assert cycles_view(run, PLAN, at(10)).remaining_s == 15 * 60


def test_a_break_taken_early_on_the_last_cycle_still_ends_in_done() -> None:
    run = CyclesRun(Phase.FOCUS, 3, start_focus(CyclesRun(), T0).clock)
    run = take_break_now(run, at(10))
    assert settle_cycles(run, PLAN, at(30))[0].phase is Phase.DONE


def test_skipping_a_break_waits_for_the_next_cycle() -> None:
    run, _ = settle_cycles(start_focus(CyclesRun(), T0), PLAN, at(50))
    assert skip_break(run, PLAN).phase is Phase.WAITING


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
