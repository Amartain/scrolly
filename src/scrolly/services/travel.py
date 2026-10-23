"""The way up to Seclusion: how often its full animation shows, whether the welcome was shown, and
whether a focus started in the room still goes on (then only the quick way up)."""

from dataclasses import dataclass
from datetime import datetime

from scrolly.domain.room_run import focus_began_in_room, run_under_way
from scrolly.domain.run_clock import check_range
from scrolly.ports import Store
from scrolly.services.seclusion_state import read_state

KEY = "travel"
DEFAULT_INTERVAL_MIN = 15  # owner, 2026-10-23: 30 was far too long
INTERVAL_MAX_MIN = 120


@dataclass(frozen=True)
class TravelView:
    interval_min: int  # minutes before the full animation shows again; 0 = every time
    welcomed: bool  # the welcome scroll was shown after the first full animation
    room_focus: bool  # a focus started in Seclusion goes on


def build_travel(store: Store) -> TravelView:
    saved = store.settings.get(KEY) or {}
    room = read_state(store)
    running = [segment.discipline for segment in store.segments.list_open()]
    under_way = run_under_way(room.discipline, room.cycles, room.flow)
    return TravelView(
        interval_min=int(saved.get("interval_min", DEFAULT_INTERVAL_MIN)),
        welcomed=bool(saved.get("welcomed", False)),
        room_focus=focus_began_in_room(running, under_way),
    )


def save_travel(
    store: Store, now: datetime, *, interval_min: int | None = None, welcomed: bool | None = None
) -> None:
    """Only what is given changes."""
    saved = dict(store.settings.get(KEY) or {})
    if interval_min is not None:
        check_range(interval_min, 0, INTERVAL_MAX_MIN, "The interval")
        saved["interval_min"] = interval_min
    if welcomed is not None:
        saved["welcomed"] = welcomed
    store.settings.set(KEY, saved, now)
