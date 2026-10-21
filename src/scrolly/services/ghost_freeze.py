"""Pausing every running timer at one moment, and starting them again from it. For ghost time.

A timer found running after a long silence is paused at the moment the app was last seen. If the
user says the silence counts, each is started again from that same moment, so nothing differs from
a timer that never stopped. A timer touched in the meantime (conquered, paused) is left alone.
"""

from dataclasses import dataclass, replace
from datetime import date, datetime
from typing import Any

from scrolly.domain import cycles, flow, planning_timer, timer
from scrolly.domain.cycles import Phase
from scrolly.domain.flow import FlowPhase
from scrolly.domain.logical_day import logical_day
from scrolly.domain.models import OPEN_STATES, Trial
from scrolly.domain.run_clock import run_pause, run_start
from scrolly.domain.segments import Discipline
from scrolly.ports import Store
from scrolly.services.seclusion_prefs import load_plan
from scrolly.services.seclusion_state import read_state, working_day, write_state
from scrolly.services.segments import sync_segments


@dataclass(frozen=True)
class Frozen:
    """What was running when it was paused."""

    trials: tuple[str, ...] = ()
    planning_day: date | None = None
    cycles: bool = False
    flow: str | None = None  # "focus" or "break"

    def __bool__(self) -> bool:
        return bool(self.trials or self.planning_day or self.cycles or self.flow)

    def to_json(self) -> dict[str, Any]:
        day = None if self.planning_day is None else self.planning_day.isoformat()
        return {
            "trials": list(self.trials),
            "planning_day": day,
            "cycles": self.cycles,
            "flow": self.flow,
        }

    @classmethod
    def from_json(cls, saved: dict[str, Any]) -> "Frozen":
        day = saved.get("planning_day")
        return cls(
            tuple(saved.get("trials", ())),
            None if day is None else date.fromisoformat(day),
            bool(saved.get("cycles")),
            saved.get("flow"),
        )


def _days(store: Store, now: datetime) -> set[date]:
    return {logical_day(now), working_day(store, now)}


def _trials(store: Store, now: datetime) -> list[Trial]:
    return [t for day in _days(store, now) for t in store.trials.list_for_day(day)]


def freeze(store: Store, at: datetime, now: datetime) -> Frozen:
    """Pause everything that is running, as of `at`."""
    running = [t for t in _trials(store, now) if t.timer_started_at is not None]
    stopped = [timer.pause(t, at) for t in running]
    store.trials.save(stopped, now)
    sync_segments(store, stopped, at)
    return Frozen(
        tuple(t.id for t in running),
        _freeze_planning(store, at, now),
        *_freeze_runs(store, at, now),
    )


def _freeze_planning(store: Store, at: datetime, now: datetime) -> date | None:
    today = logical_day(now)
    day = store.days.get(today)
    if day is None or not planning_timer.is_running(day):
        return None
    store.days.save(planning_timer.pause(day, at), now)
    return today


def _freeze_runs(store: Store, at: datetime, now: datetime) -> tuple[bool, str | None]:
    state = read_state(store)
    paused_cycles, paused_flow = False, None
    if state.discipline is Discipline.CYCLES and state.cycles.clock.running:
        run = cycles.pause_run(state.cycles, load_plan(store), at)
        state, paused_cycles = replace(state, cycles=run), True
    elif state.discipline is Discipline.FLOW and state.flow.focus.running:
        state, paused_flow = replace(state, flow=flow.pause_flow(state.flow, at)), "focus"
    elif state.discipline is Discipline.FLOW and state.flow.break_clock.running:
        bank = replace(state.flow, break_clock=run_pause(state.flow.break_clock, at))
        state, paused_flow = replace(state, flow=bank), "break"
    if paused_cycles or paused_flow:
        write_state(store, state, now)
    return paused_cycles, paused_flow


def thaw(store: Store, frozen: Frozen, at: datetime, now: datetime) -> None:
    """Start again from `at` what `freeze` paused, unless it has changed since."""
    state = read_state(store)
    by_id = {t.id: t for t in _trials(store, now)}
    untouched = [
        by_id[i]
        for i in frozen.trials
        if i in by_id and by_id[i].state in OPEN_STATES and by_id[i].timer_paused_at == at
    ]
    started = [timer.start(t, at) for t in untouched]
    store.trials.save(started, now)
    sync_segments(store, started, at, state.discipline if state.active else Discipline.DASHBOARD)
    _thaw_planning(store, frozen.planning_day, at, now)
    _thaw_runs(store, frozen, at, now)


def _thaw_planning(store: Store, planning_day: date | None, at: datetime, now: datetime) -> None:
    day = None if planning_day is None else store.days.get(planning_day)
    if day is not None and not planning_timer.is_running(day):
        store.days.save(planning_timer.start(day, at), now)


def _thaw_runs(store: Store, frozen: Frozen, at: datetime, now: datetime) -> None:
    before = read_state(store)
    state = before
    if frozen.cycles and state.discipline is Discipline.CYCLES:
        if state.cycles.phase in (Phase.FOCUS, Phase.BREAK):
            state = replace(state, cycles=cycles.resume_run(state.cycles, at))
    elif frozen.flow == "focus" and state.flow.phase is FlowPhase.FOCUS:
        bank = replace(state.flow, focus=run_start(state.flow.focus, at))
        state = replace(state, flow=bank)
    elif frozen.flow == "break" and state.flow.phase is FlowPhase.BREAK:
        bank = replace(state.flow, break_clock=run_start(state.flow.break_clock, at))
        state = replace(state, flow=bank)
    if state != before:
        write_state(store, state, now)
