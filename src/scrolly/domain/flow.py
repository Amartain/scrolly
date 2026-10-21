"""River Flow: an open-ended count-up that banks rest at a ratio. Pure, no IO.

The ratio is work : rest. At 5:1 every five focused minutes bank one minute of rest; at 1:1 every
minute does. A break counts down the whole bank; ending it early keeps what is left.
"""

from dataclasses import dataclass, field, replace
from datetime import datetime
from enum import StrEnum

from scrolly.domain.run_clock import (
    RATIO_MAX,
    RunClock,
    RunError,
    check_range,
    reached_at,
    run_elapsed,
    run_pause,
    run_start,
)

MIN_BREAK_S = 60


class FlowPhase(StrEnum):
    IDLE = "idle"
    FOCUS = "focus"
    BREAK = "break"


@dataclass(frozen=True)
class FlowBank:
    work: int = 5
    rest: int = 1
    phase: FlowPhase = FlowPhase.IDLE
    focus: RunClock = field(default_factory=RunClock)  # the focused time, which earns the rest
    used_s: int = 0  # rest already spent in earlier breaks
    break_s: int = 0  # the length of the break under way
    break_clock: RunClock = field(default_factory=RunClock)
    stretch_from_s: int = 0  # focused seconds when this stretch began (at the last break's end)


@dataclass(frozen=True)
class FlowView:
    phase: FlowPhase
    work: int
    rest: int
    focus_s: int
    banked_s: int
    break_left_s: int
    break_total_s: int
    can_break: bool  # at least a minute is banked
    break_in_s: int | None  # focus still to run before a break can start; only while focus runs
    running: bool


def focus_seconds(bank: FlowBank, now: datetime) -> int:
    return run_elapsed(bank.focus, now)


def banked_rest_s(bank: FlowBank, now: datetime) -> int:
    """Rest earned and not yet spent."""
    earned = focus_seconds(bank, now) * bank.rest // bank.work
    return max(0, earned - bank.used_s)


def set_ratio(bank: FlowBank, work: int, rest: int) -> FlowBank:
    """The ratio is fixed once a bank is open."""
    check_range(work, 1, RATIO_MAX, "The work side of the ratio")
    check_range(rest, 1, RATIO_MAX, "The rest side of the ratio")
    if bank.phase is not FlowPhase.IDLE or bank.focus.accumulated_s or bank.focus.running:
        raise RunError("The ratio cannot change while a bank is open")
    return replace(bank, work=work, rest=rest)


def start_flow(bank: FlowBank, now: datetime) -> FlowBank:
    if bank.phase is FlowPhase.BREAK:
        raise RunError("Rest first, or end the break")
    return replace(bank, phase=FlowPhase.FOCUS, focus=run_start(bank.focus, now))


def pause_flow(bank: FlowBank, now: datetime) -> FlowBank:
    settled, _ = settle_flow(bank, now)
    return replace(settled, focus=run_pause(settled.focus, now))


def start_break(bank: FlowBank, now: datetime) -> FlowBank:
    """Count the whole bank down. Needs at least a minute banked."""
    bank, _ = settle_flow(bank, now)
    banked = banked_rest_s(bank, now)
    if bank.phase is not FlowPhase.FOCUS or banked < MIN_BREAK_S:
        raise RunError("There is no rest banked yet")
    return replace(
        bank,
        phase=FlowPhase.BREAK,
        focus=run_pause(bank.focus, now),
        break_s=banked,
        break_clock=run_start(RunClock(), now),
    )


def _end_break(bank: FlowBank, spent_s: int) -> FlowBank:
    return replace(
        bank,
        phase=FlowPhase.FOCUS,  # focus waits for Start: its clock is stopped
        used_s=bank.used_s + spent_s,
        break_s=0,
        break_clock=RunClock(),
        stretch_from_s=bank.focus.accumulated_s,  # the focus clock is stopped during a break
    )


def zero_stretch(bank: FlowBank, now: datetime) -> FlowBank:
    """The stretch under way starts over from 0. Focus: the time since the last break is dropped
    (rest earned before it stays). A break: it counts the same bank down again. Running stays
    running."""
    if bank.phase is FlowPhase.BREAK:
        return replace(bank, break_clock=RunClock(now))
    if bank.phase is not FlowPhase.FOCUS:
        raise RunError("There is nothing to zero out yet")
    started = now if bank.focus.running else None
    return replace(bank, focus=RunClock(started, bank.stretch_from_s))


def end_break(bank: FlowBank, now: datetime) -> FlowBank:
    """End a break early: the rest not yet spent stays in the bank."""
    if bank.phase is not FlowPhase.BREAK:
        raise RunError("There is no break to end")
    bank, _ = settle_flow(bank, now)
    if bank.phase is not FlowPhase.BREAK:
        return bank
    return _end_break(bank, min(run_elapsed(bank.break_clock, now), bank.break_s))


def settle_flow(bank: FlowBank, now: datetime) -> tuple[FlowBank, datetime | None]:
    """A break that has run its course ends. Returns the bank and when it ended, if it did."""
    if bank.phase is FlowPhase.BREAK and (ended := reached_at(bank.break_clock, bank.break_s, now)):
        return _end_break(bank, bank.break_s), ended
    return bank, None


def flow_view(bank: FlowBank, now: datetime) -> FlowView:
    left = 0
    if bank.phase is FlowPhase.BREAK:
        left = max(0, bank.break_s - run_elapsed(bank.break_clock, now))
    running = bank.focus.running or bank.break_clock.running
    banked = banked_rest_s(bank, now)
    can_break = bank.phase is FlowPhase.FOCUS and banked >= MIN_BREAK_S
    focus = focus_seconds(bank, now)
    return FlowView(
        bank.phase,
        bank.work,
        bank.rest,
        focus,
        banked,
        left,
        bank.break_s,
        can_break,
        _break_in_s(bank, focus),
        running,
    )


def _break_in_s(bank: FlowBank, focus_s: int) -> int | None:
    """Focus seconds until a minute of rest is banked, so the screen knows when to ask again."""
    if bank.phase is not FlowPhase.FOCUS or not bank.focus.running:
        return None
    needed = -(-(MIN_BREAK_S + bank.used_s) * bank.work // bank.rest)  # ceiling
    return max(0, needed - focus_s)
