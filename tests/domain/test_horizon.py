from scrolly.domain.horizon import has_title, return_to_horizon, same_title
from scrolly.domain.models import OriginType
from tests.factories import make_item, make_trial


def test_titles_match_ignoring_case_and_outer_spaces() -> None:
    assert same_title("  Plan the Garden ", "plan the garden")
    assert not same_title("Plan the garden", "Plan the gardens")


def test_has_title() -> None:
    assert has_title([make_item("Read a book")], " READ A BOOK")
    assert not has_title([], "anything")


def test_a_returned_trial_goes_on_top() -> None:
    older = make_item("Older")
    result = return_to_horizon([older], make_trial("Mandate", is_mandate=True))
    assert [item.title for item in result] == ["Mandate", "Older"]
    assert result[0].is_mandate


def test_returning_twice_does_not_duplicate() -> None:
    trial = make_trial("Mandate", is_mandate=True)
    once = return_to_horizon([], trial)
    twice = return_to_horizon(once, trial)
    assert twice == once


def test_a_trial_summoned_from_the_horizon_updates_its_origin_in_place() -> None:
    origin = make_item("Plan", id="h1", essence_expected_min=30)
    other = make_item("Other")
    trial = make_trial(
        "Plan (renamed)",
        is_mandate=True,
        origin_type=OriginType.HORIZON,
        origin_id="h1",
        essence_expected_min=45,
    )
    result = return_to_horizon([other, origin], trial)
    assert [item.id for item in result] == ["h1", other.id]
    assert result[0].title == "Plan (renamed)"
    assert result[0].essence_expected_min == 45
