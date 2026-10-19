from scrolly.domain.essence import EssenceSummary, essence_summary
from scrolly.domain.models import TrialState
from tests.factories import make_trial


def test_an_empty_day_is_all_zero() -> None:
    assert essence_summary([]) == EssenceSummary(0, 0, 0, 0)


def test_actual_is_conquered_minutes_and_remaining_is_what_is_still_open() -> None:
    trials = [
        make_trial("A", state=TrialState.DONE, essence_expected_min=60, essence_actual_min=45),
        make_trial("B", state=TrialState.IMMEDIATE, essence_expected_min=30),
        make_trial("C", essence_expected_min=30),
    ]
    summary = essence_summary(trials)
    assert (summary.actual_min, summary.expected_min, summary.remaining_min) == (45, 120, 60)
    assert summary.meter_pct == 38


def test_postponed_and_let_go_trials_leave_the_plan() -> None:
    trials = [
        make_trial("A", state=TrialState.DONE, essence_expected_min=10, essence_actual_min=10),
        make_trial("B", state=TrialState.POSTPONED, essence_expected_min=500),
        make_trial("C", state=TrialState.LOST, essence_expected_min=500),
    ]
    assert essence_summary(trials).expected_min == 10


def test_the_meter_stops_at_full_when_the_day_ran_long() -> None:
    done = make_trial("A", state=TrialState.DONE, essence_expected_min=10, essence_actual_min=40)
    assert essence_summary([done]).meter_pct == 100


def test_trials_without_numbers_count_as_zero() -> None:
    trials = [make_trial("A", state=TrialState.DONE), make_trial("B")]
    assert essence_summary(trials) == EssenceSummary(0, 0, 0, 0)
