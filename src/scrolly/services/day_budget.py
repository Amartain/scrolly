from datetime import datetime, time

from scrolly.domain.day_budget import DEFAULT_SUNSET, DayBudget, day_budget
from scrolly.domain.logical_day import logical_day
from scrolly.ports import Store

SUNSET_KEY = "sunset"


def sunset_time(store: Store) -> time:
    """The user's sunset hour (Settings, build step 7); 21:00 until they choose one."""
    saved = store.settings.get(SUNSET_KEY)
    if saved is None:
        return DEFAULT_SUNSET
    return time(saved["hour"], saved.get("minute", 0))


def build_budget(store: Store, now: datetime) -> DayBudget:
    return day_budget(store.trials.list_for_day(logical_day(now)), now, sunset_time(store))
