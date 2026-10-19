import uuid
from datetime import datetime

from scrolly.domain.art_match import art_kind_for, with_title
from scrolly.domain.horizon import add_item, edit_item, remove_item
from scrolly.domain.logical_day import logical_day
from scrolly.domain.models import ArtKind, HorizonItem
from scrolly.domain.ordering import OrderError, reorder_by_ids
from scrolly.domain.uniqueness import require_free_trial_title
from scrolly.ports import Clock, Store


class HorizonService:
    """The user's backlog, and the order of their Arts."""

    def __init__(self, store: Store, clock: Clock) -> None:
        self._store = store
        self._clock = clock

    @property
    def _now(self) -> datetime:
        return self._clock.now()

    def _require_free(
        self, title: str, items: list[HorizonItem], except_id: str | None = None
    ) -> None:
        today = self._store.trials.list_for_day(logical_day(self._now))
        arts = self._store.arts.list_all()
        require_free_trial_title(title, items, today, arts, except_id=except_id)

    def add(self, title: str, estimate: str = "") -> None:
        current = self._store.horizon.list_all()
        self._require_free(title, current)
        kind = art_kind_for(title, self._store.arts.list_all())
        items = add_item(current, str(uuid.uuid4()), title, estimate, kind)
        self._store.horizon.replace_all(items, self._now)

    def edit(
        self,
        item_id: str,
        title: str | None = None,
        estimate: str | None = None,
        is_mandate: bool | None = None,
    ) -> None:
        current = self._store.horizon.list_all()
        if title is not None:
            self._require_free(title, current, item_id)
        items = edit_item(current, item_id, title, estimate, is_mandate)
        if title is not None:
            arts = self._store.arts.list_all()
            items = [with_title(i, i.title, arts) if i.id == item_id else i for i in items]
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
