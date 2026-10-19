import pytest

from scrolly.clock import FixedClock
from scrolly.domain.models import ArtKind
from scrolly.domain.uniqueness import DuplicateTitleError
from scrolly.ports import Store
from scrolly.services.arts import ArtsService


def test_arts_are_saved_in_order_and_survive_edits(store: Store, clock: FixedClock) -> None:
    service = ArtsService(store, clock)
    service.add(ArtKind.FOUNDATIONAL, "Stretch", "10m")
    service.add(ArtKind.RESTORATIVE, "Nap")
    service.add(ArtKind.FOUNDATIONAL, "Read")
    first = store.arts.list_all()[0]
    service.edit(first.id, title="Warm up")
    assert [a.title for a in store.arts.list_all()] == ["Warm up", "Nap", "Read"]
    assert store.arts.list_all()[0].essence_expected_min == 10


def test_a_deleted_art_is_gone_and_its_title_free(store: Store, clock: FixedClock) -> None:
    service = ArtsService(store, clock)
    service.add(ArtKind.FOUNDATIONAL, "Stretch")
    with pytest.raises(DuplicateTitleError):
        service.add(ArtKind.FOUNDATIONAL, "stretch")
    service.remove(store.arts.list_all()[0].id)
    assert store.arts.list_all() == []
    service.add(ArtKind.FOUNDATIONAL, "Stretch")
