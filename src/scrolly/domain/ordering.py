"""Putting a list in the order the user chose. Pure."""

from collections.abc import Sequence
from typing import Protocol


class OrderError(ValueError):
    """A new order that does not match the list it is for. The message is shown to the user."""


class _HasId(Protocol):
    @property
    def id(self) -> str: ...


def reorder_by_ids[T: _HasId](items: Sequence[T], ids: Sequence[str]) -> list[T]:
    """The same items in the order of `ids`, which must name each one exactly once."""
    if len(set(ids)) != len(ids) or set(ids) != {item.id for item in items}:
        raise OrderError("The new order must list every item once")
    by_id = {item.id: item for item in items}
    return [by_id[item_id] for item_id in ids]
