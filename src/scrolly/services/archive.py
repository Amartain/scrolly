from collections.abc import Callable

from scrolly.domain.archive import Archive, Tables
from scrolly.domain.logical_day import logical_day
from scrolly.domain.purge import purge_today
from scrolly.ports import Clock, Store
from scrolly.services.day import run_rollover
from scrolly.services.planning import abandon_planning


def current_tables(store: Store) -> Tables:
    """Everything the app holds, as tables, for Backup Scroll."""
    return store.archive.dump()


class ArchiveService:
    """Restore Scroll from tables, and Purge Today's Scroll."""

    def __init__(
        self, store: Store, clock: Clock, keep_copy: Callable[[Tables], None] | None = None
    ) -> None:
        self._store = store
        self._clock = clock
        self._keep_copy = keep_copy

    def restore(self, archive: Archive) -> tuple[int, int]:
        """A zip replaces everything, after a copy of what is there. A CSV adds the new rows.

        Returns (added, skipped).
        """
        now = self._clock.now()
        if archive.replaces:
            if self._keep_copy is not None:
                self._keep_copy(self._store.archive.dump())
            added, skipped = self._store.archive.replace_all(archive.tables), 0
        else:
            added, skipped = self._store.archive.add_missing(archive.tables)
        run_rollover(self._store, logical_day(now), now)
        return added, skipped

    def purge_today(self) -> None:
        """Clear today's open trials and the planning in progress. Conquered trials stay."""
        now = self._clock.now()
        store = self._store
        draft = store.drafts.get()
        if draft is not None:
            abandon_planning(store, draft, now)
        today = logical_day(now)
        day = store.days.get(today)
        if day is not None and day.first_sealed_at is not None:
            purged = purge_today(store.trials.list_for_day(today), store.horizon.list_all(), now)
            store.horizon.replace_all(purged.horizon, now)
            store.trials.delete(purged.removed)
