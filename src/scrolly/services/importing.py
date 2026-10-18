from scrolly.domain.logical_day import logical_day
from scrolly.domain.merge import Existing, ImportBatch, ImportSummary, merge_import
from scrolly.ports import Clock, Store
from scrolly.services.day import run_rollover


class ImportService:
    def __init__(self, store: Store, clock: Clock) -> None:
        self._store = store
        self._clock = clock

    def merge(self, batch: ImportBatch) -> ImportSummary:
        """Add what is missing. Open trials from past days are settled like any rollover."""
        store = self._store
        now = self._clock.now()
        today = logical_day(now)
        existing = Existing(
            trials=store.trials.list_all(),
            horizon=store.horizon.list_all(),
            arts=store.arts.list_all(),
            days=store.days.list_all(),
        )
        result = merge_import(existing, batch, today, now)
        store.trials.save(result.trials, now)
        store.horizon.replace_all(result.horizon, now)
        store.arts.save(result.arts, now)
        for day in result.days:
            store.days.save(day, now)
        run_rollover(store, today, now)
        return result.summary
