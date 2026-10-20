"""The Cycles run and the Flow bank as plain JSON, so they can live in the settings."""

from datetime import datetime
from typing import Any

from scrolly.domain.cycles import CyclesRun, Phase
from scrolly.domain.flow import FlowBank, FlowPhase
from scrolly.domain.run_clock import RunClock


def _clock_out(clock: RunClock) -> dict[str, Any]:
    started = None if clock.started_at is None else clock.started_at.isoformat()
    return {"started_at": started, "accumulated_s": clock.accumulated_s}


def _clock_in(saved: dict[str, Any] | None) -> RunClock:
    if not saved:
        return RunClock()
    started = saved.get("started_at")
    return RunClock(
        None if started is None else datetime.fromisoformat(started),
        int(saved.get("accumulated_s", 0)),
    )


def cycles_out(run: CyclesRun) -> dict[str, Any]:
    return {"phase": run.phase.value, "cycle": run.cycle, "clock": _clock_out(run.clock)}


def cycles_in(saved: dict[str, Any] | None) -> CyclesRun:
    if not saved:
        return CyclesRun()
    return CyclesRun(
        Phase(saved.get("phase", Phase.IDLE.value)),
        int(saved.get("cycle", 1)),
        _clock_in(saved.get("clock")),
    )


def flow_out(bank: FlowBank) -> dict[str, Any]:
    return {
        "work": bank.work,
        "rest": bank.rest,
        "phase": bank.phase.value,
        "focus": _clock_out(bank.focus),
        "used_s": bank.used_s,
        "break_s": bank.break_s,
        "break_clock": _clock_out(bank.break_clock),
    }


def flow_in(saved: dict[str, Any] | None, ratio: tuple[int, int]) -> FlowBank:
    """A bank never saved starts empty, at the ratio the user last chose."""
    if not saved:
        return FlowBank(*ratio)
    return FlowBank(
        int(saved["work"]),
        int(saved["rest"]),
        FlowPhase(saved.get("phase", FlowPhase.IDLE.value)),
        _clock_in(saved.get("focus")),
        int(saved.get("used_s", 0)),
        int(saved.get("break_s", 0)),
        _clock_in(saved.get("break_clock")),
    )
