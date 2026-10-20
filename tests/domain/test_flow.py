from datetime import UTC, datetime, timedelta

import pytest

from scrolly.domain.flow import (
    FlowBank,
    FlowPhase,
    banked_rest_s,
    end_break,
    flow_view,
    pause_flow,
    set_ratio,
    settle_flow,
    start_break,
    start_flow,
)
from scrolly.domain.run_clock import RunError

T0 = datetime(2026, 10, 20, 9, 0, tzinfo=UTC)


def at(minutes: float) -> datetime:
    return T0 + timedelta(minutes=minutes)


def test_every_five_focused_minutes_bank_one_at_five_to_one() -> None:
    bank = start_flow(FlowBank(5, 1), T0)
    assert banked_rest_s(bank, at(25)) == 5 * 60


def test_one_to_one_banks_every_minute() -> None:
    assert banked_rest_s(start_flow(FlowBank(1, 1), T0), at(30)) == 30 * 60


def test_three_to_two_banks_two_minutes_for_every_three() -> None:
    assert banked_rest_s(start_flow(FlowBank(3, 2), T0), at(30)) == 20 * 60


def test_nothing_banks_while_the_bank_is_paused() -> None:
    bank = pause_flow(start_flow(FlowBank(5, 1), T0), at(10))
    assert banked_rest_s(bank, at(500)) == 2 * 60


def test_a_break_counts_down_the_whole_bank() -> None:
    bank = start_break(start_flow(FlowBank(5, 1), T0), at(25))
    assert bank.phase is FlowPhase.BREAK
    view = flow_view(bank, at(27))
    assert (view.break_total_s, view.break_left_s) == (5 * 60, 3 * 60)


def test_when_the_break_runs_out_focus_waits_for_start() -> None:
    bank = start_break(start_flow(FlowBank(5, 1), T0), at(25))
    settled, ended = settle_flow(bank, at(60))
    assert ended == at(30)
    assert settled.phase is FlowPhase.FOCUS and not settled.focus.running
    assert banked_rest_s(settled, at(60)) == 0


def test_ending_a_break_early_keeps_the_unused_rest() -> None:
    bank = start_break(start_flow(FlowBank(5, 1), T0), at(25))
    bank = end_break(bank, at(27))
    assert bank.phase is FlowPhase.FOCUS
    assert banked_rest_s(bank, at(27)) == 3 * 60


def test_work_after_a_break_banks_on_top_of_what_was_left() -> None:
    bank = end_break(start_break(start_flow(FlowBank(5, 1), T0), at(25)), at(27))
    bank = start_flow(bank, at(30))
    assert banked_rest_s(bank, at(40)) == 5 * 60  # 3 min kept + 2 min earned


def test_a_break_needs_a_minute_banked() -> None:
    with pytest.raises(RunError):
        start_break(start_flow(FlowBank(5, 1), T0), at(4))


def test_the_ratio_is_fixed_once_the_bank_is_open() -> None:
    with pytest.raises(RunError):
        set_ratio(start_flow(FlowBank(5, 1), T0), 3, 2)
    assert set_ratio(FlowBank(), 3, 2) == FlowBank(3, 2)


@pytest.mark.parametrize("work, rest", [(0, 1), (11, 1), (1, 0), (1, 11)])
def test_a_ratio_side_outside_one_to_ten_is_refused(work: int, rest: int) -> None:
    with pytest.raises(RunError):
        set_ratio(FlowBank(), work, rest)
