from dataclasses import dataclass, replace
from datetime import datetime

from scrolly.domain.day_flow import TrialError, immediate_of
from scrolly.domain.logical_day import logical_day
from scrolly.domain.models import Trial, TrialState
from scrolly.domain.seclusion import IncenseView, incense_view, ring_elapsed, seconds_to_gong
from scrolly.domain.segments import Discipline
from scrolly.domain.timer import elapsed_seconds
from scrolly.ports import Clock, Store
from scrolly.services.dashboard_view import TimerView
from scrolly.services.day import run_rollover
from scrolly.services.seclusion_state import read_state, working_day, write_state
from scrolly.services.today import TodayService


@dataclass(frozen=True)
class SeclusionView:
    active: bool
    discipline: Discipline
    trial: Trial | None
    timer: TimerView | None
    ring_elapsed_s: int
    incense: IncenseView | None  # None until the trial has an estimate
    gong_in_s: int | None  # only while the timer runs and there is an estimate
    remaining: list[Trial]


class SeclusionService:
    """The focus room: one trial, its timer, nothing else. Time is paced, never punished."""

    def __init__(self, store: Store, clock: Clock) -> None:
        self._store = store
        self._clock = clock
        self._today = TodayService(store, clock)

    @property
    def _now(self) -> datetime:
        return self._clock.now()

    def _trials(self) -> list[Trial]:
        return self._store.trials.list_for_day(working_day(self._store, self._now))

    def _immediate(self) -> Trial:
        trial = immediate_of(self._trials())
        if trial is None:
            raise TrialError("There is no trial to focus on")
        return trial

    def enter(self) -> None:
        state = read_state(self._store)
        if state.active:
            return
        trial = self._immediate()
        day = logical_day(self._now)
        write_state(self._store, replace(state, active=True, day=day), self._now)
        if trial.timer_started_at is not None:
            self._restart(trial)  # a timer already running continues here as an Incense segment

    def leave(self) -> None:
        """Stepping out pauses the trial. A scroll held open past 04:00 now rolls over."""
        state = read_state(self._store)
        if not state.active:
            return
        trial = immediate_of(self._trials())
        if trial is not None:
            self._today.pause_timer(trial.id)
        write_state(self._store, replace(state, active=False), self._now)
        run_rollover(self._store, logical_day(self._now), self._now)

    def _restart(self, trial: Trial) -> None:
        self._today.pause_timer(trial.id)
        self._today.start_timer(trial.id, Discipline.INCENSE)

    def start(self) -> None:
        self._today.start_timer(self._immediate().id, Discipline.INCENSE)

    def pause(self) -> None:
        self._today.pause_timer(self._immediate().id)

    def new_timer(self) -> None:
        """A fresh timer on the same trial: the ring starts over, the logged time stays."""
        trial = self._immediate()
        self._set_baseline(trial)
        self._restart(trial)

    def zero_out(self) -> None:
        """Stop and clear the ring. The time already logged on the trial stays."""
        trial = self._immediate()
        self._today.pause_timer(trial.id)
        self._set_baseline(trial)

    def _set_baseline(self, trial: Trial) -> None:
        state = read_state(self._store)
        baselines = {**state.baselines, trial.id: elapsed_seconds(trial, self._now)}
        write_state(self._store, replace(state, baselines=baselines), self._now)

    def view(self) -> SeclusionView:
        state = read_state(self._store)
        now = self._now
        trials = self._trials()
        trial = immediate_of(trials)
        remaining = sorted(
            (t for t in trials if t.state is TrialState.REMAINING), key=lambda t: t.position
        )
        if trial is None:
            return SeclusionView(
                state.active, Discipline.INCENSE, None, None, 0, None, None, remaining
            )
        elapsed = elapsed_seconds(trial, now)
        running = trial.timer_started_at is not None
        expected = None if trial.essence_expected_min is None else trial.essence_expected_min * 60
        ring = ring_elapsed(elapsed, state.baselines.get(trial.id, 0))
        return SeclusionView(
            active=state.active,
            discipline=Discipline.INCENSE,
            trial=trial,
            timer=TimerView(elapsed, running, expected),
            ring_elapsed_s=ring,
            incense=None if expected is None else incense_view(ring, expected),
            gong_in_s=seconds_to_gong(ring, expected) if running and expected else None,
            remaining=remaining,
        )
