from datetime import datetime

import pytest

from scrolly.domain.models import (
    Art,
    ArtKind,
    Day,
    OriginType,
    PlanningDraft,
    PlanPhase,
    PlanStatus,
    TrialState,
)
from scrolly.domain.planning import (
    abandon,
    dismiss,
    dump_lines,
    next_position,
    planning_status,
    trial_from_art,
    trial_from_horizon,
    trial_from_line,
    unstage,
)
from tests.factories import DAY, make_item, make_trial

NOW = datetime.fromisoformat("2026-10-18T09:00:00+02:00")


def test_status_follows_the_seal_then_the_draft() -> None:
    sealed = Day(logical_day=DAY, first_sealed_at=NOW)
    draft = PlanningDraft(logical_day=DAY, phase=PlanPhase.ESTIMATE)
    assert planning_status(None, None) is PlanStatus.ZERO
    assert planning_status(Day(logical_day=DAY), None) is PlanStatus.ZERO
    assert planning_status(None, PlanningDraft(logical_day=DAY)) is PlanStatus.INSCRIBE
    assert planning_status(Day(logical_day=DAY), draft) is PlanStatus.ESTIMATE
    assert planning_status(sealed, None) is PlanStatus.ACTIVE
    assert planning_status(sealed, draft) is PlanStatus.ACTIVE


def test_dump_lines_keeps_one_trial_per_non_empty_line() -> None:
    assert dump_lines("  Coffee \n\n   \nRead chapter 1\r\n") == ["Coffee", "Read chapter 1"]
    assert dump_lines("") == []


def test_positions_continue_after_the_last_trial() -> None:
    assert next_position([]) == 0
    assert next_position([make_trial("a", position=4), make_trial("b", position=2)]) == 5


def test_a_dump_line_becomes_a_mortal_trial() -> None:
    trial = trial_from_line("t1", "Coffee", DAY, 3)
    assert (trial.state, trial.is_mandate, trial.origin_type) == (
        TrialState.REMAINING,
        False,
        OriginType.BRAIN_DUMP,
    )
    assert trial.position == 3 and trial.essence_expected_min is None


def test_a_horizon_item_keeps_its_data_and_remembers_its_origin() -> None:
    item = make_item("Plan", id="h1", is_mandate=True, essence_expected_min=45, note="n")
    trial = trial_from_horizon("t1", item, DAY, 0)
    assert trial.is_mandate and trial.essence_expected_min == 45 and trial.note == "n"
    assert (trial.origin_type, trial.origin_id) == (OriginType.HORIZON, "h1")


def test_an_art_copy_is_never_a_mandate_and_remembers_the_template() -> None:
    art = Art(id="a1", kind=ArtKind.RESTORATIVE, title="Tea", essence_expected_min=20)
    trial = trial_from_art("t1", art, DAY, 0)
    assert not trial.is_mandate and trial.essence_expected_min == 20
    assert (trial.origin_type, trial.origin_id) == (OriginType.RESTORATIVE_ART, "a1")
    foundational = Art(id="a2", kind=ArtKind.FOUNDATIONAL, title="Stretch")
    assert trial_from_art("t2", foundational, DAY, 0).origin_type is OriginType.FOUNDATIONAL_ART


def test_unstaging_a_horizon_trial_puts_the_item_back_on_top_with_its_old_id() -> None:
    item = make_item("Plan", id="h1")
    trial = trial_from_horizon("t1", item, DAY, 0)
    result = unstage(trial, [make_item("Other")])
    assert [i.id for i in result] == ["h1", "item-Other"]
    assert result[0].title == "Plan"


@pytest.mark.parametrize("kind", [ArtKind.FOUNDATIONAL, ArtKind.RESTORATIVE])
def test_unstaging_an_art_copy_or_a_dump_line_leaves_the_horizon_alone(kind: ArtKind) -> None:
    horizon = [make_item("Other")]
    art = trial_from_art("t1", Art(id="a", kind=kind, title="Art"), DAY, 0)
    assert unstage(art, horizon) == horizon
    assert unstage(trial_from_line("t2", "line", DAY, 0), horizon) == horizon


def test_abandon_gives_back_every_horizon_item_and_nothing_else() -> None:
    first = trial_from_horizon("t1", make_item("One", id="h1"), DAY, 0)
    second = trial_from_horizon("t2", make_item("Two", id="h2"), DAY, 1)
    line = trial_from_line("t3", "line", DAY, 2)
    result = abandon([first, second, line], [])
    assert {i.id for i in result} == {"h1", "h2"}


def test_dismissing_a_mortal_trial_loses_it_without_touching_the_horizon() -> None:
    trial, horizon = dismiss(make_trial("Walk"), [make_item("Other")])
    assert trial.state is TrialState.LOST
    assert [i.title for i in horizon] == ["Other"]


def test_dismissing_a_mandate_postpones_it_to_the_top_of_the_horizon() -> None:
    mandate = make_trial("Taxes", is_mandate=True)
    trial, horizon = dismiss(mandate, [make_item("Other")])
    assert trial.state is TrialState.POSTPONED
    assert [i.title for i in horizon] == ["Taxes", "Other"]


def test_dismissing_a_mandate_twice_does_not_duplicate_it() -> None:
    mandate = make_trial("Taxes", is_mandate=True)
    _, once = dismiss(mandate, [])
    _, twice = dismiss(mandate, once)
    assert twice == once
