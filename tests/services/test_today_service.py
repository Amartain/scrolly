from dataclasses import replace
from datetime import timedelta

import pytest

from scrolly.clock import FixedClock
from scrolly.domain.day_flow import TrialError
from scrolly.domain.models import TrialState
from scrolly.ports import Store
from scrolly.services.dashboard_view import build_dashboard_view
from scrolly.services.golden_core import build_qi_view
from scrolly.services.today import TodayService
from tests.factories import DAY
from tests.services.flow import by_title, seal_day, states


def test_sealing_makes_the_first_trial_immediate(store: Store, clock: FixedClock) -> None:
    seal_day(store, clock, "A", "B")
    assert build_dashboard_view(store, clock.now()).immediate is not None


def test_conquering_promotes_the_next_trial_and_lists_the_conquest(
    store: Store, clock: FixedClock
) -> None:
    today = seal_day(store, clock, "A", "B", "C")
    today.conquer(by_title(store)["A"].id)
    assert states(store) == {
        "A": TrialState.DONE,
        "B": TrialState.IMMEDIATE,
        "C": TrialState.REMAINING,
    }
    assert [t.title for t in build_dashboard_view(store, clock.now()).conquered] == ["A"]


def test_conquered_trials_read_in_the_order_they_were_conquered(
    store: Store, clock: FixedClock
) -> None:
    today = seal_day(store, clock, "A", "B", "C")
    today.conquer(by_title(store)["A"].id)
    clock.set(clock.now() + timedelta(minutes=10))
    today.conquer(by_title(store)["B"].id)
    titles = [t.title for t in build_dashboard_view(store, clock.now()).conquered]
    assert titles == ["A", "B"]


def test_conquering_the_last_trial_is_a_victory(store: Store, clock: FixedClock) -> None:
    today = seal_day(store, clock, "A")
    assert not build_dashboard_view(store, clock.now()).victory
    today.conquer(by_title(store)["A"].id)
    view = build_dashboard_view(store, clock.now())
    assert (view.victory, view.immediate) == (True, None)


def test_conquered_qi_counts_as_spent_and_reviving_gives_it_back(
    store: Store, clock: FixedClock
) -> None:
    today = seal_day(store, clock, "A", "B")
    a = by_title(store)["A"]
    store.trials.save([replace(a, qi_expected=40)], clock.now())
    assert build_qi_view(store, clock.now()).spent == 0
    today.conquer(a.id)
    assert build_qi_view(store, clock.now()).spent == 40
    today.revive(a.id)
    assert build_qi_view(store, clock.now()).spent == 0


def test_postponing_puts_a_mandate_on_top_of_the_horizon_and_promotes(
    store: Store, clock: FixedClock
) -> None:
    today = seal_day(store, clock, "A", "B")
    a = by_title(store)["A"]
    today.update(a.id, is_mandate=True)
    today.postpone(a.id)
    assert [item.title for item in store.horizon.list_all()] == ["A"]
    assert states(store) == {"A": TrialState.POSTPONED, "B": TrialState.IMMEDIATE}


def test_abandoning_a_mortal_lets_it_go_and_a_mandate_is_refused(
    store: Store, clock: FixedClock
) -> None:
    today = seal_day(store, clock, "A", "B")
    a = by_title(store)["A"]
    today.update(a.id, is_mandate=True)
    with pytest.raises(TrialError, match="Postpone"):
        today.abandon(a.id)
    today.update(a.id, is_mandate=False)
    today.abandon(a.id)
    assert states(store) == {"A": TrialState.LOST, "B": TrialState.IMMEDIATE}


def test_reviving_with_another_underway_goes_to_the_top_of_the_queue(
    store: Store, clock: FixedClock
) -> None:
    today = seal_day(store, clock, "A", "B", "C")
    a = by_title(store)["A"]
    today.conquer(a.id)
    today.revive(a.id)
    assert states(store) == {
        "A": TrialState.REMAINING,
        "B": TrialState.IMMEDIATE,
        "C": TrialState.REMAINING,
    }
    waiting = sorted(
        (t for t in store.trials.list_for_day(DAY) if t.state is TrialState.REMAINING),
        key=lambda t: t.position,
    )
    assert [t.title for t in waiting] == ["A", "C"]


def test_a_conquered_minutes_figure_can_be_corrected(store: Store, clock: FixedClock) -> None:
    today = seal_day(store, clock, "A", "B")
    a = by_title(store)["A"]
    today.conquer(a.id)
    today.update(a.id, actual="1h15m")
    assert by_title(store)["A"].essence_actual_min == 75


def test_nothing_can_be_done_before_the_day_is_sealed(store: Store, clock: FixedClock) -> None:
    with pytest.raises(TrialError, match="not begun"):
        TodayService(store, clock).conquer("anything")


def test_an_unknown_trial_is_refused(store: Store, clock: FixedClock) -> None:
    today = seal_day(store, clock, "A")
    with pytest.raises(TrialError, match="not on today"):
        today.conquer("nope")


def test_renaming_changes_the_title(store: Store, clock: FixedClock) -> None:
    today = seal_day(store, clock, "A")
    today.update(by_title(store)["A"].id, title="  Better title ")
    assert list(by_title(store)) == ["Better title"]
