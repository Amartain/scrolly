"""Whether Seclusion is open and on which day's scroll, kept in the settings."""

from datetime import date, datetime, timedelta

from scrolly.domain.logical_day import logical_day
from scrolly.ports import Store

KEY = "seclusion"


def held_day(store: Store, today: date) -> date | None:
    """Yesterday's scroll, kept open while Seclusion is open past 04:00.

    The running trial stays where it is until the user steps out; only then does the rollover run.
    """
    state = store.settings.get(KEY)
    if not state or not state.get("active"):
        return None
    day = date.fromisoformat(state["day"])
    return day if day == today - timedelta(days=1) else None


def working_day(store: Store, now: datetime) -> date:
    """The day whose scroll the user is working on: the held one, else today."""
    today = logical_day(now)
    return held_day(store, today) or today
