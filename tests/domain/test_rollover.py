from datetime import date, datetime, timedelta

from hypothesis import given
from hypothesis import strategies as st

from scrolly.domain.models import HorizonItem, Trial, TrialState
from scrolly.domain.rollover import rollover
from tests.factories import make_item, make_trial

TODAY = date(2026, 10, 18)
YESTERDAY = date(2026, 10, 17)
NOW = datetime.fromisoformat("2026-10-18T04:30:00+02:00")


def test_an_unfinished_mortal_trial_is_lost_to_time() -> None:
    result = rollover([make_trial("Walk", logical_day=YESTERDAY)], [], TODAY, NOW)
    assert [t.state for t in result.changed] == [TrialState.LOST]
    assert result.horizon == []


def test_an_unfinished_mandate_returns_to_the_horizon() -> None:
    mandate = make_trial("Taxes", logical_day=YESTERDAY, is_mandate=True)
    result = rollover([mandate], [make_item("Old")], TODAY, NOW)
    assert [t.state for t in result.changed] == [TrialState.RETURNED]
    assert [item.title for item in result.horizon] == ["Taxes", "Old"]


def test_a_mandate_already_on_the_horizon_is_not_duplicated() -> None:
    mandate = make_trial("Taxes", logical_day=YESTERDAY, is_mandate=True)
    first = rollover([mandate], [], TODAY, NOW)
    again = rollover([mandate], first.horizon, TODAY, NOW)
    assert again.horizon == first.horizon


def test_finished_and_postponed_trials_stay_as_they_are() -> None:
    kept = [
        make_trial("Done", logical_day=YESTERDAY, state=TrialState.DONE),
        make_trial("Later", logical_day=YESTERDAY, state=TrialState.POSTPONED),
        make_trial("Gone", logical_day=YESTERDAY, state=TrialState.LOST),
    ]
    assert rollover(kept, [], TODAY, NOW).changed == []


def test_todays_trials_are_never_touched() -> None:
    today = [make_trial("Now", state=TrialState.IMMEDIATE), make_trial("Next", is_mandate=True)]
    result = rollover(today, [], TODAY, NOW)
    assert result.changed == [] and result.horizon == []


def test_a_running_timer_is_stopped_and_kept() -> None:
    running = make_trial(
        "Walk", logical_day=YESTERDAY, timer_started_at=NOW - timedelta(seconds=600)
    )
    (lost,) = rollover([running], [], TODAY, NOW).changed
    assert lost.timer_started_at is None and lost.timer_accumulated_s == 600


def test_a_mandate_returns_to_the_horizon_with_the_time_worked() -> None:
    running = make_trial(
        "Taxes",
        logical_day=YESTERDAY,
        is_mandate=True,
        timer_accumulated_s=300,
        timer_started_at=NOW - timedelta(seconds=600),
    )
    result = rollover([running], [], TODAY, NOW)
    assert result.horizon[0].worked_s == 900


def test_mandates_keep_their_order_on_top_of_the_horizon() -> None:
    first = make_trial("First", logical_day=YESTERDAY, is_mandate=True, position=0)
    second = make_trial("Second", logical_day=YESTERDAY, is_mandate=True, position=1)
    result = rollover([second, first], [], TODAY, NOW)
    assert [item.title for item in result.horizon] == ["First", "Second"]


def _apply(trials: list[Trial], changed: list[Trial]) -> list[Trial]:
    by_id = {t.id: t for t in changed}
    return [by_id.get(t.id, t) for t in trials]


trial_strategy = st.builds(
    make_trial,
    title=st.text(min_size=1, max_size=5),
    id=st.uuids().map(str),
    logical_day=st.sampled_from([date(2026, 10, 15), YESTERDAY, TODAY]),
    state=st.sampled_from(list(TrialState)),
    is_mandate=st.booleans(),
    position=st.integers(0, 5),
)


@given(st.lists(trial_strategy, max_size=8, unique_by=lambda t: t.id))
def test_a_second_rollover_changes_nothing_and_no_mandate_vanishes(trials: list[Trial]) -> None:
    horizon: list[HorizonItem] = []
    first = rollover(trials, horizon, TODAY, NOW)
    settled = _apply(trials, first.changed)
    second = rollover(settled, first.horizon, TODAY, NOW)
    assert second.changed == []
    assert second.horizon == first.horizon
    returned_titles = {
        t.title
        for t in trials
        if t.is_mandate
        and t.logical_day < TODAY
        and t.state in {TrialState.IMMEDIATE, TrialState.REMAINING}
    }
    assert returned_titles <= {item.title for item in first.horizon}
