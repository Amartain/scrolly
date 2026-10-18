from datetime import datetime, time

from scrolly.domain.day_budget import DEFAULT_SUNSET, day_budget, light_left
from scrolly.domain.models import TrialState
from tests.factories import make_trial


def at(text: str) -> datetime:
    return datetime.fromisoformat(f"2026-10-18T{text}:00+02:00")


def test_an_empty_scroll_plans_nothing() -> None:
    budget = day_budget([], at("13:00"), DEFAULT_SUNSET)
    assert (budget.trial_count, budget.planned_min, budget.light_min) == (0, 0, 480)
    assert budget.beyond_light_min == 0


def test_time_splits_into_mandate_and_mortal() -> None:
    trials = [
        make_trial("a", essence_expected_min=60, is_mandate=True),
        make_trial("b", essence_expected_min=30),
        make_trial("c", essence_expected_min=15),
    ]
    budget = day_budget(trials, at("13:00"), DEFAULT_SUNSET)
    assert (budget.planned_min, budget.mandate_min, budget.mortal_min) == (105, 60, 45)


def test_trials_without_an_estimate_are_counted_but_add_no_minutes() -> None:
    trials = [make_trial("a", essence_expected_min=20), make_trial("b")]
    budget = day_budget(trials, at("13:00"), DEFAULT_SUNSET)
    assert (budget.trial_count, budget.planned_min, budget.unestimated_count) == (2, 20, 1)


def test_only_open_trials_are_planned() -> None:
    trials = [
        make_trial("a", essence_expected_min=20),
        make_trial("b", essence_expected_min=40, state=TrialState.LOST),
        make_trial("c", essence_expected_min=50, state=TrialState.DONE),
    ]
    assert day_budget(trials, at("13:00"), DEFAULT_SUNSET).planned_min == 20


def test_planning_more_than_the_light_left_is_counted_as_beyond() -> None:
    trials = [make_trial("a", essence_expected_min=300)]
    budget = day_budget(trials, at("18:00"), DEFAULT_SUNSET)
    assert (budget.light_min, budget.beyond_light_min) == (180, 120)


def test_exactly_at_sunset_there_is_no_light_left() -> None:
    assert light_left(at("21:00"), DEFAULT_SUNSET) is None
    assert light_left(at("20:59"), DEFAULT_SUNSET) == 1


def test_after_sunset_nothing_is_beyond() -> None:
    trials = [make_trial("a", essence_expected_min=300)]
    budget = day_budget(trials, at("22:30"), DEFAULT_SUNSET)
    assert (budget.light_min, budget.beyond_light_min) == (None, 0)


def test_the_small_hours_still_belong_to_the_previous_logical_day() -> None:
    assert light_left(datetime.fromisoformat("2026-10-19T02:00:00+02:00"), DEFAULT_SUNSET) is None


def test_a_sunset_after_midnight_counts_into_the_next_calendar_day() -> None:
    assert light_left(at("23:00"), time(1, 0)) == 120
