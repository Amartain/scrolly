from datetime import datetime

from scrolly.domain.day_budget import DayBudget, day_budget
from scrolly.domain.logical_day import logical_day
from scrolly.domain.sunset import budget_sunset
from scrolly.ports import Store
from scrolly.services.sunset import load_prefs


def build_budget(store: Store, now: datetime) -> DayBudget:
    sunset = budget_sunset(load_prefs(store))
    return day_budget(store.trials.list_for_day(logical_day(now)), now, sunset)
