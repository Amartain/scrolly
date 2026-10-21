"""The user's own corrections of a time: scrapping a timer's minutes, a conquered trial's time."""

from datetime import UTC, datetime, timedelta

import pytest

from scrolly.domain.cycles import CyclesRun, Phase, restart_run, start_focus, zero_phase
from scrolly.domain.day_flow import TrialError, set_actual_minutes
from scrolly.domain.duration import DurationError
from scrolly.domain.flow import (
    FlowBank,
    FlowPhase,
    banked_rest_s,
    end_break,
    focus_seconds,
    pause_flow,
    start_break,
    start_flow,
    zero_stretch,
)
from scrolly.domain.models import TrialState
from scrolly.domain.run_clock import RunClock, RunError, run_elapsed
from scrolly.domain.seclusion import since_mark
from scrolly.domain.timer import elapsed_seconds, scrap
from tests.factories import make_trial

T0 = datetime(2026, 10, 20, 9, 0, tzinfo=UTC)


def at(minutes: float) -> datetime:
    return T0 + timedelta(minutes=minutes)


def test_scrapping_a_paused_timer_takes_the_minutes_off() -> None:
    scrapped = scrap(make_trial(timer_accumulated_s=600), 240, T0)
    assert (scrapped.timer_accumulated_s, scrapped.timer_started_at) == (360, None)


def test_a_running_timer_keeps_running_from_the_corrected_total() -> None:
    running = make_trial(timer_started_at=at(-10))
    scrapped = scrap(running, 4 * 60, T0)
    assert scrapped.timer_started_at == T0
    assert elapsed_seconds(scrapped, at(1)) == 7 * 60


def test_scrapping_never_goes_below_zero() -> None:
    assert scrap(make_trial(timer_accumulated_s=60), 600, T0).timer_accumulated_s == 0


def test_time_since_a_mark_is_none_without_one() -> None:
    assert since_mark(27 * 60, 20 * 60) == 7 * 60
    assert since_mark(27 * 60, None) == 0


def test_zero_out_starts_the_cycle_under_way_over_and_keeps_its_number() -> None:
    run = CyclesRun(Phase.FOCUS, 2, RunClock(at(-27)))
    zeroed = zero_phase(run, T0)
    assert (zeroed.phase, zeroed.cycle) == (Phase.FOCUS, 2)
    assert zeroed.clock.running and run_elapsed(zeroed.clock, T0) == 0


def test_zero_out_of_a_paused_cycle_stays_paused() -> None:
    zeroed = zero_phase(CyclesRun(Phase.FOCUS, 1, RunClock(None, 600)), T0)
    assert zeroed.clock == RunClock()


def test_zero_out_before_a_cycle_begins_is_refused() -> None:
    for phase in (Phase.IDLE, Phase.WAITING, Phase.DONE):
        with pytest.raises(RunError):
            zero_phase(CyclesRun(phase), T0)


def test_restart_begins_the_first_cycle_at_once() -> None:
    run = restart_run(T0)
    assert (run.phase, run.cycle, run.clock.running) == (Phase.FOCUS, 1, True)
    assert start_focus(CyclesRun(), T0).clock == run.clock


def test_zero_out_of_a_flow_drops_only_the_focus_since_the_last_break() -> None:
    bank = start_flow(FlowBank(1, 1), T0)
    bank = start_break(bank, at(10))  # ten minutes banked, all spent on a break
    bank = end_break(bank, at(12))  # two of them rested
    bank = start_flow(bank, at(12))
    zeroed = zero_stretch(bank, at(20))  # eight minutes of this stretch are dropped
    assert focus_seconds(zeroed, at(20)) == 10 * 60
    assert zeroed.focus.running
    assert banked_rest_s(zeroed, at(20)) == 8 * 60  # earned before the stretch, less the rest taken


def test_zero_out_of_a_paused_flow_stays_paused() -> None:
    bank = pause_flow(start_flow(FlowBank(5, 1), T0), at(5))
    zeroed = zero_stretch(bank, at(9))
    assert (focus_seconds(zeroed, at(9)), zeroed.focus.running) == (0, False)


def test_zero_out_during_a_flow_break_counts_the_same_bank_down_again() -> None:
    bank = start_break(start_flow(FlowBank(1, 1), T0), at(10))
    zeroed = zero_stretch(bank, at(13))
    assert (zeroed.phase, zeroed.break_s) == (FlowPhase.BREAK, 10 * 60)
    assert run_elapsed(zeroed.break_clock, at(13)) == 0


def test_zero_out_of_an_empty_flow_is_refused() -> None:
    with pytest.raises(RunError):
        zero_stretch(FlowBank(), T0)


def test_a_conquered_trials_time_can_be_corrected() -> None:
    done = make_trial(state=TrialState.DONE, essence_actual_min=27, timer_accumulated_s=27 * 60)
    for text, minutes in (("45m", 45), ("+1h5m", 65), (" 2h ", 120)):
        fixed = set_actual_minutes(done, text)
        assert (fixed.essence_actual_min, fixed.timer_accumulated_s) == (minutes, minutes * 60)


def test_only_a_conquered_trial_and_a_real_time_are_taken() -> None:
    with pytest.raises(TrialError):
        set_actual_minutes(make_trial(state=TrialState.REMAINING), "45m")
    done = make_trial(state=TrialState.DONE, essence_actual_min=27)
    with pytest.raises(TrialError):
        set_actual_minutes(done, "  ")
    for bad in ("0m", "45", "17h"):
        with pytest.raises(DurationError):
            set_actual_minutes(done, bad)
