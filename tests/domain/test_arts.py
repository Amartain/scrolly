import pytest

from scrolly.domain import arts
from scrolly.domain.arts import ArtError
from scrolly.domain.duration import DurationError
from scrolly.domain.models import Art, ArtKind
from scrolly.domain.uniqueness import DuplicateTitleError

STRETCH = Art(id="a1", kind=ArtKind.FOUNDATIONAL, title="Stretch", essence_expected_min=10)


def test_add_trims_the_title_and_reads_the_duration() -> None:
    art = arts.add([], "a2", ArtKind.RESTORATIVE, "  Nap ", "1h30m")
    assert (art.title, art.kind, art.essence_expected_min) == ("Nap", ArtKind.RESTORATIVE, 90)


def test_a_blank_duration_means_none() -> None:
    assert arts.add([], "a2", ArtKind.FOUNDATIONAL, "Nap").essence_expected_min is None


def test_add_needs_a_title() -> None:
    with pytest.raises(ArtError):
        arts.add([], "a2", ArtKind.FOUNDATIONAL, "   ")


def test_a_title_is_unique_in_its_own_list_only() -> None:
    with pytest.raises(DuplicateTitleError):
        arts.add([STRETCH], "a2", ArtKind.FOUNDATIONAL, " stretch")
    arts.add([STRETCH], "a2", ArtKind.RESTORATIVE, "Stretch")


def test_a_bad_duration_is_refused() -> None:
    with pytest.raises(DurationError):
        arts.add([], "a2", ArtKind.FOUNDATIONAL, "Nap", "90")


def test_edit_changes_only_what_is_given() -> None:
    renamed = arts.edit([STRETCH], "a1", title="Warm up")
    assert (renamed.title, renamed.essence_expected_min) == ("Warm up", 10)
    retimed = arts.edit([STRETCH], "a1", estimate="2h")
    assert (retimed.title, retimed.essence_expected_min) == ("Stretch", 120)
    assert arts.edit([STRETCH], "a1", estimate="").essence_expected_min is None


def test_edit_may_keep_its_own_title_but_not_take_another() -> None:
    other = Art(id="a2", kind=ArtKind.FOUNDATIONAL, title="Read")
    arts.edit([STRETCH, other], "a1", title="STRETCH")
    with pytest.raises(DuplicateTitleError):
        arts.edit([STRETCH, other], "a1", title="read")


def test_edit_and_remove_need_an_existing_art() -> None:
    with pytest.raises(ArtError):
        arts.edit([], "nope", title="x")
    with pytest.raises(ArtError):
        arts.remove([], "nope")
    assert arts.remove([STRETCH], "a1") == STRETCH
