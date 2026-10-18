from datetime import datetime

import pytest
from hypothesis import given
from hypothesis import strategies as st

from scrolly.domain.duration import DurationError
from scrolly.domain.models import Art, ArtKind, Day, Trial, TrialState
from scrolly.domain.planning import (
    PlanningError,
    reorder,
    seal,
    set_estimate,
    set_mandate,
    trial_from_art,
)
from tests.factories import DAY, make_trial

NOW = datetime.fromisoformat("2026-10-18T09:00:00+02:00")


def test_estimates_parse_and_blank_clears() -> None:
    trial = make_trial("a", essence_expected_min=30)
    assert set_estimate(trial, "1h15m").essence_expected_min == 75
    assert set_estimate(trial, "").essence_expected_min is None
    with pytest.raises(DurationError):
        set_estimate(trial, "soon")


def test_mandate_toggle_is_refused_for_arts_only() -> None:
    art = trial_from_art("t", Art(id="a", kind=ArtKind.FOUNDATIONAL, title="Art"), DAY, 0)
    with pytest.raises(PlanningError):
        set_mandate(art, True)
    assert not set_mandate(art, False).is_mandate
    assert set_mandate(make_trial("a"), True).is_mandate


def test_reorder_sets_positions_in_the_given_order() -> None:
    trials = [make_trial("a", position=0), make_trial("b", position=1), make_trial("c", position=2)]
    result = reorder(trials, ["trial-c", "trial-a", "trial-b"])
    assert [(t.title, t.position) for t in result] == [("c", 0), ("a", 1), ("b", 2)]


@pytest.mark.parametrize(
    "ids", [["trial-a"], ["trial-a", "trial-a"], ["trial-a", "trial-b", "other"], []]
)
def test_reorder_rejects_any_other_set_of_ids(ids: list[str]) -> None:
    trials = [make_trial("a"), make_trial("b")]
    with pytest.raises(PlanningError):
        reorder(trials, ids)


@given(
    st.lists(st.uuids().map(str), min_size=1, max_size=8, unique=True).flatmap(
        lambda ids: st.permutations(ids).map(lambda order: (ids, list(order)))
    )
)
def test_reorder_keeps_exactly_the_same_trials(case: tuple[list[str], list[str]]) -> None:
    ids, order = case
    trials = [make_trial(f"t{i}", id=trial_id, position=i) for i, trial_id in enumerate(ids)]
    result = reorder(trials, order)
    assert [t.id for t in result] == order
    assert [t.position for t in result] == list(range(len(ids)))


def test_sealing_makes_the_lowest_position_immediate_and_stamps_the_day() -> None:
    trials = [make_trial("b", position=2), make_trial("a", position=1)]
    first, day = seal(trials, Day(logical_day=DAY), NOW)
    assert first.title == "a" and first.state is TrialState.IMMEDIATE
    assert day.first_sealed_at == NOW


def test_only_the_first_seal_of_a_day_is_stamped() -> None:
    earlier = datetime.fromisoformat("2026-10-18T05:00:00+02:00")
    _, day = seal([make_trial("a")], Day(logical_day=DAY, first_sealed_at=earlier), NOW)
    assert day.first_sealed_at == earlier


def test_sealing_an_empty_scroll_is_refused() -> None:
    with pytest.raises(PlanningError):
        seal([], Day(logical_day=DAY), NOW)
    done = make_trial("done", state=TrialState.DONE)
    with pytest.raises(PlanningError):
        seal([done], Day(logical_day=DAY), NOW)


@given(st.lists(st.integers(0, 20), min_size=1, max_size=8, unique=True))
def test_sealing_leaves_exactly_one_immediate_trial(positions: list[int]) -> None:
    trials = [make_trial(f"t{p}", position=p) for p in positions]
    first, _ = seal(trials, Day(logical_day=DAY), NOW)
    changed: list[Trial] = [first] + [t for t in trials if t.id != first.id]
    assert sum(t.state is TrialState.IMMEDIATE for t in changed) == 1
    assert first.position == min(positions)
