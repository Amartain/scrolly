from collections.abc import Callable
from dataclasses import replace

from scrolly.domain.archive import Tables
from scrolly.domain.logical_day import logical_day
from scrolly.domain.models import Day
from scrolly.domain.restart import restart_today
from scrolly.domain.rollover import rollover
from scrolly.domain.secret_seals import Seal, SealKind, parse_seal
from scrolly.domain.sunset import FINISHED
from scrolly.ports import Clock, Store
from scrolly.services.segments import sync_segments


class SealService:
    """The Secret Seal Inscription. Each seal changes the day in a way ordinary use never does."""

    def __init__(
        self, store: Store, clock: Clock, keep_copy: Callable[[Tables], None] | None = None
    ) -> None:
        self._store = store
        self._clock = clock
        self._keep_copy = keep_copy

    def inscribe(self, text: str) -> Seal | None:
        """Do what the words ask. None if they name no seal. A day-number seal only names the day:
        the milestone is built by the caller."""
        seal = parse_seal(text)
        if seal is None:
            return None
        now = self._clock.now()
        today = logical_day(now)
        day = self._store.days.get(today) or Day(logical_day=today)
        if seal.kind is SealKind.DUSK:
            # Dusk is forced for the day, and its poem may be read again.
            self._store.days.save(replace(day, dusk_override=FINISHED, poem_shown_at=None), now)
        elif seal.kind is SealKind.SUNRISE:
            self._store.days.save(replace(day, dusk_override=None), now)
        elif seal.kind is SealKind.ROLLOVER:
            self._run_rollover(day)
        elif seal.kind is SealKind.RESTART:
            self._restart(day)
        return seal

    def _run_rollover(self, day: Day) -> None:
        """What happens at 04:00, now: open trials are settled and the day's flags are reset."""
        now = self._clock.now()
        today = logical_day(now)
        trials = self._store.trials.list_for_day(today)
        tomorrow = today.fromordinal(today.toordinal() + 1)
        result = rollover(trials, self._store.horizon.list_all(), tomorrow, now)
        if result.changed:
            self._store.trials.save(result.changed, now)
            sync_segments(self._store, result.changed, now)
            self._store.horizon.replace_all(result.horizon, now)
        self._store.days.save(replace(day, dusk_override=None, advisor_silenced=False), now)

    def _restart(self, day: Day) -> None:
        """Today starts over at the zero state. A copy of the data is kept first."""
        now = self._clock.now()
        if self._keep_copy is not None:
            self._keep_copy(self._store.archive.dump())
        today = logical_day(now)
        trials = self._store.trials.list_for_day(today)
        restarted = restart_today(trials, self._store.horizon.list_all(), day, now)
        self._store.horizon.replace_all(restarted.horizon, now)
        self._store.trials.delete(restarted.removed)
        self._store.drafts.delete()
        self._store.days.save(restarted.day, now)
