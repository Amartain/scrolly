"""Whether Seclusion is open and on which day's scroll, kept in the settings."""

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta

from scrolly.domain.logical_day import logical_day
from scrolly.ports import Store

KEY = "seclusion"


@dataclass(frozen=True)
class SeclusionState:
    active: bool = False
    day: date | None = None
    # Logged seconds at the last New timer or Zero out, per trial: the ring counts from there.
    baselines: dict[str, int] = field(default_factory=dict)


def read_state(store: Store) -> SeclusionState:
    saved = store.settings.get(KEY)
    if not saved:
        return SeclusionState()
    day = saved.get("day")
    return SeclusionState(
        active=bool(saved.get("active")),
        day=None if day is None else date.fromisoformat(day),
        baselines={k: int(v) for k, v in saved.get("baselines", {}).items()},
    )


def write_state(store: Store, state: SeclusionState, now: datetime) -> None:
    saved = {
        "active": state.active,
        "day": None if state.day is None else state.day.isoformat(),
        "baselines": state.baselines,
    }
    store.settings.set(KEY, saved, now)


def held_day(store: Store, today: date) -> date | None:
    """Yesterday's scroll, kept open while Seclusion is open past 04:00.

    The running trial stays where it is until the user steps out; only then does the rollover run.
    """
    state = read_state(store)
    if not state.active or state.day is None:
        return None
    return state.day if state.day == today - timedelta(days=1) else None


def working_day(store: Store, now: datetime) -> date:
    """The day whose scroll the user is working on: the held one, else today."""
    today = logical_day(now)
    return held_day(store, today) or today
