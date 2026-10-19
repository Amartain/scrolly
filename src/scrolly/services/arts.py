import uuid
from datetime import datetime

from scrolly.domain import arts
from scrolly.domain.models import ArtKind
from scrolly.ports import Clock, Store


class ArtsService:
    """The user's practices: add, edit and delete Arts (ordering lives in HorizonService)."""

    def __init__(self, store: Store, clock: Clock) -> None:
        self._store = store
        self._clock = clock

    @property
    def _now(self) -> datetime:
        return self._clock.now()

    def add(self, kind: ArtKind, title: str, estimate: str = "") -> None:
        art = arts.add(self._store.arts.list_all(), str(uuid.uuid4()), kind, title, estimate)
        self._store.arts.save([art], self._now)

    def edit(self, art_id: str, title: str | None = None, estimate: str | None = None) -> None:
        art = arts.edit(self._store.arts.list_all(), art_id, title, estimate)
        self._store.arts.save([art], self._now)

    def remove(self, art_id: str) -> None:
        art = arts.remove(self._store.arts.list_all(), art_id)
        self._store.arts.delete([art.id])
