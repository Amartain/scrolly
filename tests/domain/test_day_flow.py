from dataclasses import replace
from datetime import datetime, timedelta
from typing import Any

import pytest

from scrolly.domain.day_flow import (
    TrialError,
    abandon,
    conquer,
    is_victory,
    postpone,
    promote_next,
    rename,
    require_editable,
    revive,
    set_estimate,
)
from scrolly.domain.models import ArtKind, Day, OriginType, Trial, TrialState
from scrolly.domain.planning import trial_from_horizon
from scrolly.domain.timer import start
from tests.factories import make_item, make_trial

NOW = datetime.fromisoformat("2026-10-18T13:00:00+02:00")
SEALED = Day(logical_day=NOW.date(), first_sealed_at=NOW)


def _immediate(**fields: Any) -> Trial:
    return make_trial("Now", state=TrialState.IMMEDIATE, **fields)


def test_conquering_a_timed_trial_records_the_timed_minutes_and_stops_the_timer() -> None:
    trial = start(_immediate(essence_expected_min=45), NOW - timedelta(minutes=31))
    done = conquer(trial, NOW)
    assert (done.state, done.essence_actual_min, done.completed_at) == (TrialState.DONE, 31, NOW)
    assert done.timer_started_at is None
    assert done.timer_accumulated_s == 31 * 60


def test_conquering_without_a_timer_records_the_estimate() -> None:
    assert conquer(_immediate(essence_expected_min=45), NOW).essence_actual_min == 45


def test_conquering_without_a_timer_or_estimate_records_nothing() -> None:
    assert conquer(_immediate(), NOW).essence_actual_min is None


def test_only_the_immediate_trial_can_be_conquered() -> None:
    with pytest.raises(TrialError):
        conquer(make_trial("Waiting"), NOW)


def test_the_first_remaining_trial_is_promoted_when_nothing_is_underway() -> None:
    later = make_trial("Later", position=2)
    first = make_trial("First", position=1)
    changed = promote_next([later, first, make_trial("Done", state=TrialState.DONE)])
    assert [(t.title, t.state) for t in changed] == [("First", TrialState.IMMEDIATE)]


def test_nothing_is_promoted_while_a_trial_is_underway_or_none_wait() -> None:
    assert promote_next([_immediate(), make_trial("Waiting")]) == []
    assert promote_next([make_trial("Done", state=TrialState.DONE)]) == []


def test_postponing_goes_to_the_top_of_the_horizon_with_the_estimate_and_the_time_worked() -> None:
    trial = start(_immediate(essence_expected_min=45, is_mandate=True), NOW - timedelta(minutes=5))
    gone, horizon = postpone(trial, [make_item("Old")], NOW)
    assert gone.state is TrialState.POSTPONED
    assert gone.timer_started_at is None
    assert [item.title for item in horizon] == ["Now", "Old"]
    assert (horizon[0].essence_expected_min, horizon[0].is_mandate) == (45, True)
    assert horizon[0].worked_s == 5 * 60


def test_an_art_instance_carries_no_time_to_the_horizon() -> None:
    trial = start(_immediate(art_kind=ArtKind.FOUNDATIONAL), NOW - timedelta(minutes=5))
    _, horizon = postpone(trial, [], NOW)
    assert horizon[0].worked_s == 0


def test_summoned_back_a_postponed_trial_resumes_from_the_time_worked() -> None:
    trial = start(_immediate(), NOW - timedelta(minutes=5))
    _, horizon = postpone(trial, [], NOW)
    again = trial_from_horizon("t2", horizon[0], NOW.date(), 0)
    assert again.timer_accumulated_s == 5 * 60
    assert again.timer_started_at is None
    # Postponed a second day, the earlier time is not lost or counted twice.
    resumed = start(again, NOW)
    _, horizon = postpone(resumed, [], NOW + timedelta(minutes=2))
    assert horizon[0].worked_s == 7 * 60


def test_postponing_onto_an_existing_item_adds_the_time() -> None:
    trial = start(_immediate(), NOW - timedelta(minutes=5))
    existing = make_item("Now", id="h1", worked_s=60)
    waiting = replace(trial, origin_type=OriginType.HORIZON, origin_id="h1")
    _, horizon = postpone(waiting, [existing], NOW)
    assert horizon[0].worked_s == 6 * 60


def test_postponing_twice_updates_the_horizon_item_instead_of_adding_one() -> None:
    trial = _immediate(origin_id="item-Now", origin_type=OriginType.HORIZON)
    _, horizon = postpone(trial, [make_item("Now")], NOW)
    assert [item.title for item in horizon] == ["Now"]


def test_a_mortal_trial_can_be_abandoned_and_its_timer_stops() -> None:
    lost = abandon(start(_immediate(), NOW - timedelta(minutes=5)), NOW)
    assert (lost.state, lost.timer_started_at) == (TrialState.LOST, None)


def test_a_heavenly_mandate_cannot_be_abandoned() -> None:
    with pytest.raises(TrialError, match="Postpone"):
        abandon(_immediate(is_mandate=True), NOW)


def test_reviving_with_nothing_underway_makes_it_immediate_and_clears_the_record() -> None:
    done = make_trial(
        "Done",
        state=TrialState.DONE,
        essence_actual_min=30,
        completed_at=NOW,
        timer_accumulated_s=1800,
    )
    back = revive(done, [done])
    assert back.state is TrialState.IMMEDIATE
    assert (back.essence_actual_min, back.completed_at) == (None, None)
    assert back.timer_accumulated_s == 1800


def test_reviving_while_another_is_underway_goes_to_the_top_of_the_queue() -> None:
    done = make_trial("Done", state=TrialState.DONE)
    queue = [_immediate(position=0), make_trial("A", position=1), make_trial("B", position=2)]
    back = revive(done, [done, *queue])
    assert (back.state, back.position) == (TrialState.REMAINING, -1)


def test_only_a_conquered_trial_can_be_revived() -> None:
    with pytest.raises(TrialError):
        revive(make_trial("Waiting"), [])


def test_a_conquered_trial_is_read_only() -> None:
    with pytest.raises(TrialError, match="Revive"):
        require_editable(make_trial("Done", state=TrialState.DONE))
    require_editable(make_trial("Waiting"))


def test_renaming_trims_and_refuses_an_empty_title() -> None:
    assert rename(make_trial("Old"), "  New  ").title == "New"
    with pytest.raises(TrialError):
        rename(make_trial("Old"), "   ")


def test_victory_needs_a_sealed_day_something_conquered_and_nothing_open() -> None:
    done = make_trial("Done", state=TrialState.DONE)
    assert is_victory(SEALED, [done])
    assert not is_victory(SEALED, [done, make_trial("Waiting")])
    assert not is_victory(SEALED, [done, _immediate()])
    assert not is_victory(None, [done])
    assert not is_victory(Day(logical_day=NOW.date()), [done])


def test_a_day_where_everything_was_let_go_is_not_a_victory() -> None:
    assert not is_victory(SEALED, [make_trial("Gone", state=TrialState.LOST)])
    assert not is_victory(SEALED, [])


def test_the_time_estimate_is_set_once() -> None:
    assert set_estimate(make_trial("A"), "45m").essence_expected_min == 45
    assert set_estimate(make_trial("A"), "").essence_expected_min is None
    with pytest.raises(TrialError, match="already set"):
        set_estimate(make_trial("A", essence_expected_min=30), "1h")
    with pytest.raises(TrialError):
        set_estimate(make_trial("A", state=TrialState.DONE), "1h")
