from dataclasses import dataclass, replace
from datetime import date, datetime, timedelta

from scrolly.domain import qi
from scrolly.domain.logical_day import logical_day
from scrolly.domain.models import PlanningDraft, PlanPhase
from scrolly.domain.qi import QiDay, QiOutlook
from scrolly.ports import Clock, Store

KEY = "golden_core"


@dataclass(frozen=True)
class GoldenCoreSetting:
    enabled: bool = False
    invited: bool = False


@dataclass(frozen=True)
class QiView:
    enabled: bool
    invited: bool
    planned: int
    start: int
    low: int
    high: int
    redline: int
    tomorrow_start: int


def read_setting(store: Store) -> GoldenCoreSetting:
    saved = store.settings.get(KEY)
    if saved is None:
        return GoldenCoreSetting()
    return GoldenCoreSetting(enabled=saved["enabled"], invited=saved["invited"])


def qi_history(store: Store, today: date) -> list[QiDay]:
    """Recent days the Golden Core was used: the chosen start and the Qi actually spent."""
    oldest = today - timedelta(days=qi.HISTORY_DAYS)
    return [
        QiDay(day.logical_day, day.qi_start, qi.spent(store.trials.list_for_day(day.logical_day)))
        for day in store.days.list_all()
        if day.qi_start is not None and oldest <= day.logical_day < today
    ]


def todays_outlook(store: Store, today: date) -> QiOutlook:
    return qi.outlook(qi_history(store, today), today)


def chosen_start(store: Store, draft: PlanningDraft | None, today: date) -> int:
    """The start the user picked for the day being planned, or the suggested one."""
    available = todays_outlook(store, today)
    if draft is None or draft.qi_start is None:
        return available.start
    return min(max(draft.qi_start, available.low), available.high)


def build_qi_view(store: Store, now: datetime) -> QiView:
    today = logical_day(now)
    setting = read_setting(store)
    available = todays_outlook(store, today)
    day = store.days.get(today)
    if day is not None and day.qi_start is not None:
        start = day.qi_start
    else:
        start = chosen_start(store, store.drafts.get(), today)
    planned = qi.planned(store.trials.list_for_day(today))
    return QiView(
        enabled=setting.enabled,
        invited=setting.invited,
        planned=planned,
        start=start,
        low=available.low,
        high=available.high,
        redline=qi.redline(start),
        tomorrow_start=qi.next_start(available.strain, start, planned),
    )


class GoldenCoreService:
    def __init__(self, store: Store, clock: Clock) -> None:
        self._store = store
        self._clock = clock

    def setting(self) -> GoldenCoreSetting:
        return read_setting(self._store)

    def set_enabled(self, enabled: bool) -> None:
        """Either answer to the invitation retires it. Switching off while weighing steps back."""
        now = self._clock.now()
        self._store.settings.set(KEY, {"enabled": enabled, "invited": True}, now)
        draft = self._store.drafts.get()
        if not enabled and draft is not None and draft.phase is PlanPhase.WEIGH:
            self._store.drafts.save(replace(draft, phase=PlanPhase.ESTIMATE, qi_start=None), now)
