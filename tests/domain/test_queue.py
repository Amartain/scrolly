from datetime import datetime, timedelta

import pytest

from scrolly.domain.day_flow import TrialError, abandon, postpone
from scrolly.domain.models import Trial, TrialState
from scrolly.domain.queue import promote, reorder_remaining, scribe
from scrolly.domain.timer import start
from tests.factories import make_trial

NOW = datetime.fromisoformat("2026-10-18T13:00:00+02:00")
DAY = NOW.date()


def _day() -> list[Trial]:
    return [
        make_trial("Now", state=TrialState.IMMEDIATE, position=0),
        make_trial("B", state=TrialState.REMAINING, position=1),
        make_trial("C", state=TrialState.REMAINING, position=2),
    ]


def _by_title(trials: list[Trial], title: str) -> Trial:
    return next(t for t in trials if t.title == title)


def test_a_scribed_trial_waits_at_the_end_while_one_is_underway() -> None:
    trial = scribe("n", "  Pay rent ", "20m", "15", DAY, _day())
    assert (trial.state, trial.position, trial.title) == (TrialState.REMAINING, 3, "Pay rent")
    assert (trial.essence_expected_min, trial.qi_expected) == (20, 15)


def test_a_scribed_trial_is_immediate_when_nothing_is_underway() -> None:
    assert scribe("n", "Pay rent", "", "", DAY, []).state is TrialState.IMMEDIATE


def test_scribing_needs_a_title_and_a_valid_estimate() -> None:
    with pytest.raises(TrialError):
        scribe("n", "   ", "", "", DAY, [])
    with pytest.raises(ValueError, match="45m"):
        scribe("n", "x", "soon", "", DAY, [])


def test_promoting_swaps_with_the_immediate_trial_which_goes_to_the_top() -> None:
    trials = _day()
    trials[0] = start(trials[0], NOW - timedelta(minutes=10))
    changed = promote(_by_title(trials, "C"), trials, NOW)
    promoted, stepped_back = _by_title(changed, "C"), _by_title(changed, "Now")
    assert promoted.state is TrialState.IMMEDIATE
    assert stepped_back.state is TrialState.REMAINING
    assert stepped_back.position < min(t.position for t in trials if t.title in ("B", "C"))
    assert stepped_back.timer_started_at is None and stepped_back.timer_accumulated_s == 600


def test_promoting_with_nothing_underway_only_changes_that_trial() -> None:
    trials = [t for t in _day() if t.title != "Now"]
    assert [t.title for t in promote(trials[0], trials, NOW)] == ["B"]


def test_only_a_remaining_trial_can_be_promoted() -> None:
    trials = _day()
    with pytest.raises(TrialError):
        promote(trials[0], trials, NOW)


def test_reordering_the_waiting_trials_reuses_their_positions() -> None:
    changed = reorder_remaining(_day(), [_day()[2].id, _day()[1].id])
    assert {t.title: t.position for t in changed} == {"C": 1, "B": 2}


def test_a_new_order_must_list_every_waiting_trial_once() -> None:
    trials = _day()
    for bad in ([trials[1].id], [trials[1].id, trials[1].id], [trials[0].id, trials[1].id]):
        with pytest.raises(TrialError):
            reorder_remaining(trials, bad)


def test_a_waiting_trial_can_be_postponed_or_abandoned() -> None:
    trial = _day()[1]
    assert postpone(trial, [], NOW)[0].state is TrialState.POSTPONED
    assert abandon(trial, NOW).state is TrialState.LOST
    done = make_trial("d", state=TrialState.DONE)
    with pytest.raises(TrialError):
        abandon(done, NOW)
