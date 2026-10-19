import uuid
from datetime import datetime

from scrolly.domain.horizon import add_item, edit_item, remove_item
from scrolly.domain.models import ArtKind
from scrolly.domain.ordering import OrderError, reorder_by_ids
from scrolly.ports import Clock, Store


class HorizonService:
    """The user's backlog, and the order of their Arts."""

    def __init__(self, store: Store, clock: Clock) -> None:
        self._store = store
        self._clock = clock

    @property
    def _now(self) -> datetime:
        return self._clock.now()

    def add(self, title: str) -> None:
        items = add_item(self._store.horizon.list_all(), str(uuid.uuid4()), title)
        self._store.horizon.replace_all(items, self._now)

    def edit(
        self,
        item_id: str,
        title: str | None = None,
        estimate: str | None = None,
        is_mandate: bool | None = None,
    ) -> None:
        items = edit_item(self._store.horizon.list_all(), item_id, title, estimate, is_mandate)
        self._store.horizon.replace_all(items, self._now)

    def discard(self, item_id: str) -> None:
        items = remove_item(self._store.horizon.list_all(), item_id)
        self._store.horizon.replace_all(items, self._now)

    def reorder(self, ids: list[str]) -> None:
        items = reorder_by_ids(self._store.horizon.list_all(), ids)
        self._store.horizon.replace_all(items, self._now)

    def reorder_arts(self, kind: ArtKind, ids: list[str]) -> None:
        """Reorder the Arts of one kind; the other kind keeps its place."""
        arts = self._store.arts.list_all()
        mine = [a for a in arts if a.kind is kind]
        if len(set(ids)) != len(ids) or set(ids) != {a.id for a in mine}:
            raise OrderError("The new order must list every Art once")
        ordered = iter(reorder_by_ids(mine, ids))
        merged = [next(ordered) if a.kind is kind else a for a in arts]
        self._store.arts.set_order([a.id for a in merged], self._now)
