import pytest

from scrolly.domain.models import Art, ArtKind, TrialState
from scrolly.domain.uniqueness import (
    DuplicateTitleError,
    Place,
    Refusal,
    art_title_taken,
    require_free_art_title,
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


@pytest.mark.parametrize("kind", list(ArtKind))
def test_art_instances_never_block_a_title(kind: ArtKind) -> None:
    on_scroll = [make_trial("Stretch", art_kind=kind)]
    on_horizon = [make_item("Stretch", art_kind=kind)]
    assert trial_title_taken("Stretch", [], on_scroll) is None
    assert trial_title_taken("Stretch", on_horizon, []) is None


def test_a_title_naming_an_art_is_never_taken() -> None:
    arts = [Art(id="a1", kind=ArtKind.FOUNDATIONAL, title="Walk")]
    assert trial_title_taken("walk", HORIZON, [make_trial("Walk")], arts) is None
    require_free_trial_title(" WALK ", HORIZON, [make_trial("Walk")], arts)


def test_a_dump_may_repeat_art_lines_but_nothing_else() -> None:
    arts = [Art(id="a1", kind=ArtKind.FOUNDATIONAL, title="Carry Water")]
    require_free_dump(
        ["Carry Water", "carry water", "Walk"], HORIZON, [make_trial("Carry Water")], arts
    )
    with pytest.raises(DuplicateTitleError, match="Written twice: walk"):
        require_free_dump(["Carry Water", "Walk", "walk"], HORIZON, [], arts)


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


def test_a_refusal_carries_the_facts_for_the_interface() -> None:
    with pytest.raises(DuplicateTitleError) as caught:
        require_free_trial_title(" taxes ", HORIZON, [])
    assert caught.value.refusal == Refusal(horizon=["taxes"])
    with pytest.raises(DuplicateTitleError) as caught:
        require_free_trial_title("Walk", [], [make_trial("Walk")])
    assert caught.value.refusal == Refusal(today=["Walk"])


def test_an_art_refusal_and_a_dump_refusal_carry_their_titles() -> None:
    arts = [Art(id="a1", kind=ArtKind.FOUNDATIONAL, title="Stretch")]
    with pytest.raises(DuplicateTitleError) as caught:
        require_free_art_title("stretch", arts, ArtKind.FOUNDATIONAL)
    assert caught.value.refusal == Refusal(art=["stretch"])
    lines = ["Taxes", "Walk", "walk", "Read"]
    with pytest.raises(DuplicateTitleError) as caught:
        require_free_dump(lines, HORIZON, [make_trial("Read")])
    assert caught.value.refusal == Refusal(repeated=["walk"], horizon=["Taxes"], today=["Read"])
