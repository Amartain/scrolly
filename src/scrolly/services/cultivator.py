"""Where the cultivator of the peak is, kept in the settings and settled when a view is built."""

from datetime import date, datetime

from scrolly.domain.cultivator import Cultivator, PeakFacts, settle_cultivator
from scrolly.domain.models import OPEN_STATES
from scrolly.domain.room_run import run_under_way
from scrolly.ports import Store
from scrolly.services.seclusion_state import read_state, working_day

KEY = "cultivator"


def _read(store: Store) -> Cultivator:
    saved = store.settings.get(KEY) or {}
    day = saved.get("day")
    return Cultivator(
        up=bool(saved.get("up")),
        day=None if day is None else date.fromisoformat(day),
        run_seen=bool(saved.get("run_seen")),
    )


def on_peak(store: Store, now: datetime) -> bool:
    """True while the cultivator meditates on the peak. Written only when something changed."""
    day = working_day(store, now)
    trials = store.trials.list_for_day(day)
    room = read_state(store)
    facts = PeakFacts(
        day=day,
        timer_running=any(t.timer_started_at is not None for t in trials),
        run_under_way=run_under_way(room.discipline, room.cycles, room.flow),
        trials_left=any(t.state in OPEN_STATES for t in trials),
    )
    was = _read(store)
    settled = settle_cultivator(was, facts)
    if settled != was:
        saved = {"up": settled.up, "day": day.isoformat(), "run_seen": settled.run_seen}
        store.settings.set(KEY, saved, now)
    return settled.up
