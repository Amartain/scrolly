"""Bamboo Scraps: the scrap of this visit to Seclusion, opened on entering and closed on leaving."""

import uuid
from datetime import datetime

from scrolly.domain import scraps
from scrolly.domain.day_flow import TrialError
from scrolly.domain.scraps import Scrap
from scrolly.ports import Clock, Store
from scrolly.services.seclusion_state import read_state


class ScrapService:
    def __init__(self, store: Store, clock: Clock) -> None:
        self._store = store
        self._clock = clock

    @property
    def _now(self) -> datetime:
        return self._clock.now()

    def _current(self) -> Scrap | None:
        return next((s for s in self._store.scraps.list_all() if s.is_open), None)

    def _keep_or_drop(self, scrap: Scrap) -> None:
        if scraps.is_kept(scrap):
            self._store.scraps.save(scrap, self._now)
        else:
            self._store.scraps.delete(scrap.id)

    def open(self) -> None:
        """A visit begins. A scrap left open by a crash is closed where it was last saved."""
        stale = self._current()
        if stale is not None:
            self._keep_or_drop(scraps.close_after_crash(stale))
        self._store.scraps.save(scraps.open_scrap(str(uuid.uuid4()), self._now), self._now)

    def close(self) -> None:
        """The visit ends. A scrap with nothing written on it is not kept."""
        current = self._current()
        if current is not None:
            self._keep_or_drop(scraps.close_scrap(current, self._now))

    def text(self) -> str:
        current = self._current()
        return "" if current is None else current.text

    def write(self, text: str) -> None:
        if not read_state(self._store).active:
            raise TrialError("Bamboo Scraps are written inside Seclusion")
        current = self._current()
        if current is None:
            self.open()
            current = self._current()
        assert current is not None
        self._store.scraps.save(scraps.write_scrap(current, text, self._now), self._now)

    def note_trial(self, trial_id: str) -> None:
        """A trial was started during this visit."""
        current = self._current()
        if current is not None:
            self._store.scraps.save(scraps.note_trial(current, trial_id), self._now)
