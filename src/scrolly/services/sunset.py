from datetime import datetime

from scrolly.domain.logical_day import logical_day
from scrolly.domain.sunset import SunsetPrefs, parse_sunset_time, settle_finished
from scrolly.ports import Clock, Store

KEY = "sunset"


def load_prefs(store: Store) -> SunsetPrefs:
    """The saved choice. A saved hour from before the invitation existed counts as an answer."""
    saved = store.settings.get(KEY)
    if saved is None:
        return SunsetPrefs()
    return SunsetPrefs(
        enabled=saved.get("enabled", True),
        invited=saved.get("invited", True),
        hour=saved.get("hour", SunsetPrefs.hour),
        minute=saved.get("minute", 0),
        chime=saved.get("chime", False),
    )


def settle_day(store: Store, now: datetime) -> None:
    """After a trial leaves the open list: if that finished the day, dusk stays for the day."""
    today = logical_day(now)
    day = store.days.get(today)
    settled = settle_finished(day, store.trials.list_for_day(today))
    if settled is not None and settled != day:
        store.days.save(settled, now)


class SunsetService:
    def __init__(self, store: Store, clock: Clock) -> None:
        self._store = store
        self._clock = clock

    def choose(
        self,
        enabled: bool | None = None,
        at: str | None = None,
        chime: bool | None = None,
    ) -> SunsetPrefs:
        """Only what is given changes. Giving a time or a yes/no answers the invitation."""
        current = load_prefs(self._store)
        hour, minute = current.hour, current.minute
        if at is not None:
            parsed = parse_sunset_time(at)
            hour, minute = parsed.hour, parsed.minute
        answered = enabled is not None or at is not None
        prefs = SunsetPrefs(
            enabled=current.enabled or at is not None if enabled is None else enabled,
            invited=current.invited or answered,
            hour=hour,
            minute=minute,
            chime=current.chime if chime is None else chime,
        )
        self._store.settings.set(
            KEY,
            {
                "enabled": prefs.enabled,
                "invited": prefs.invited,
                "hour": prefs.hour,
                "minute": prefs.minute,
                "chime": prefs.chime,
            },
            self._clock.now(),
        )
        self._store.commit()
        return prefs
