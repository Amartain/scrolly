import pytest

from scrolly.domain.models import Art, ArtKind, OriginType, TrialState
from scrolly.domain.uniqueness import (
    DuplicateTitleError,
    Place,
    art_title_taken,
    require_free_dump,
    require_free_trial_title,
    trial_title_taken,
)
from tests.factories import make_item, make_trial

HORIZON = [make_item("Taxes")]


def test_a_title_on_the_horizon_is_taken_ignoring_case_and_spaces() -> None:
    assert trial_title_taken("  taxes ", HORIZON, []) is Place.HORIZON


@pytest.mark.parametrize("state", [TrialState.IMMEDIATE, TrialState.REMAINING, TrialState.DONE])
def test_a_title_on_todays_scroll_is_taken(state: TrialState) -> None:
    assert trial_title_taken("Walk", [], [make_trial("Walk", state=state)]) is Place.TODAY


@pytest.mark.parametrize("state", [TrialState.LOST, TrialState.POSTPONED, TrialState.RETURNED])
def test_fallen_leaves_and_postponed_trials_free_the_title(state: TrialState) -> None:
    assert trial_title_taken("Walk", [], [make_trial("Walk", state=state)]) is None


def test_an_earlier_day_does_not_block_a_title() -> None:
    # Earlier days are never passed in: the service lists today's trials only.
    assert trial_title_taken("Walk", [], []) is None


@pytest.mark.parametrize("origin", [OriginType.FOUNDATIONAL_ART, OriginType.RESTORATIVE_ART])
def test_art_copies_never_block_a_title(origin: OriginType) -> None:
    assert trial_title_taken("Stretch", [], [make_trial("Stretch", origin_type=origin)]) is None


def test_renaming_ignores_the_item_itself() -> None:
    assert trial_title_taken("Taxes", HORIZON, [], except_id="item-Taxes") is None
    trial = make_trial("Walk")
    assert trial_title_taken("walk", [], [trial], except_id=trial.id) is None


def test_the_refusal_names_the_place() -> None:
    with pytest.raises(DuplicateTitleError, match="Already on the Horizon"):
        require_free_trial_title("Taxes", HORIZON, [])
    with pytest.raises(DuplicateTitleError, match="Already on today's scroll"):
        require_free_trial_title("Walk", [], [make_trial("Walk")])


def test_art_titles_are_unique_within_a_kind_only() -> None:
    arts = [Art(id="a1", kind=ArtKind.FOUNDATIONAL, title="Stretch")]
    assert art_title_taken(" STRETCH", arts, ArtKind.FOUNDATIONAL)
    assert not art_title_taken("Stretch", arts, ArtKind.RESTORATIVE)
    assert not art_title_taken("Stretch", arts, ArtKind.FOUNDATIONAL, except_id="a1")


def test_a_dump_names_every_repeat_and_every_existing_title() -> None:
    lines = ["Taxes", "Walk", "walk", "Call mum", "Read"]
    with pytest.raises(DuplicateTitleError) as caught:
        require_free_dump(lines, HORIZON, [make_trial("Read")])
    assert str(caught.value) == (
        "Written twice: walk. Already on the Horizon: Taxes. Already on today's scroll: Read"
    )


def test_a_clean_dump_passes() -> None:
    require_free_dump(["A", "B"], HORIZON, [make_trial("C")])
