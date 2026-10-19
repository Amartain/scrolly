import pytest

from scrolly.domain.duration import DurationError
from scrolly.domain.horizon import HorizonError, add_item, edit_item, remove_item
from scrolly.domain.models import HorizonItem
from scrolly.domain.ordering import OrderError, reorder_by_ids

ITEMS = [HorizonItem(id="a", title="A", essence_expected_min=30), HorizonItem(id="b", title="B")]


def test_a_new_idea_goes_on_top_with_a_trimmed_title() -> None:
    assert [i.title for i in add_item(ITEMS, "n", "  New  ")] == ["New", "A", "B"]


def test_a_new_idea_can_carry_an_estimate() -> None:
    assert add_item(ITEMS, "n", "New", "1h30m")[0].essence_expected_min == 90
    assert add_item(ITEMS, "n", "New", "")[0].essence_expected_min is None
    assert add_item(ITEMS, "n", "New")[0].essence_expected_min is None


def test_a_bad_estimate_is_never_saved() -> None:
    for bad in ("90", "1.5h", "0m", "17h"):
        with pytest.raises(DurationError):
            add_item(ITEMS, "n", "New", bad)


def test_an_idea_needs_a_title() -> None:
    with pytest.raises(HorizonError):
        add_item(ITEMS, "n", "  ")


def test_editing_changes_only_what_is_given() -> None:
    edited = edit_item(ITEMS, "a", "Renamed", None)
    assert (edited[0].title, edited[0].essence_expected_min) == ("Renamed", 30)
    assert edit_item(ITEMS, "a", None, "1h")[0].essence_expected_min == 60
    assert edit_item(ITEMS, "a", None, "")[0].essence_expected_min is None
    assert edited[1] == ITEMS[1]


def test_editing_or_removing_a_missing_item_is_refused() -> None:
    with pytest.raises(HorizonError):
        edit_item(ITEMS, "zzz", "x", None)
    with pytest.raises(HorizonError):
        remove_item(ITEMS, "zzz")


def test_removing_keeps_the_rest_in_order() -> None:
    assert [i.id for i in remove_item(ITEMS, "a")] == ["b"]


def test_reordering_by_ids() -> None:
    assert [i.id for i in reorder_by_ids(ITEMS, ["b", "a"])] == ["b", "a"]
    for bad in (["a"], ["a", "a"], ["a", "c"]):
        with pytest.raises(OrderError):
            reorder_by_ids(ITEMS, bad)


def test_an_idea_can_become_a_mandate_and_back() -> None:
    made = edit_item(ITEMS, "b", is_mandate=True)
    assert made[1].is_mandate and not made[0].is_mandate
    assert not edit_item(made, "b", is_mandate=False)[1].is_mandate
