from datetime import timedelta

import pytest

from scrolly.clock import FixedClock
from scrolly.domain.day_flow import TrialError
from scrolly.ports import Store
from scrolly.services.dashboard_view import build_dashboard_view
from scrolly.storage.store import SqliteStores
from tests.services.flow import by_title, seal_day


def test_the_timer_counts_from_two_timestamps_across_stores_and_a_long_gap(
    stores: SqliteStores, clock: FixedClock
) -> None:
    with stores() as first:
        today = seal_day(first, clock, "A")
        today.start_timer(by_title(first)["A"].id)
    clock.set(clock.now() + timedelta(minutes=20))
    with stores() as later:
        timer = build_dashboard_view(later, clock.now()).timer
    assert timer is not None
    assert (timer.elapsed_s, timer.running) == (1200, True)


def test_pausing_stops_the_count_and_resuming_continues_it(
    stores: SqliteStores, clock: FixedClock
) -> None:
    with stores() as store:
        today = seal_day(store, clock, "A")
        trial_id = by_title(store)["A"].id
        today.start_timer(trial_id)
        clock.set(clock.now() + timedelta(minutes=10))
        today.pause_timer(trial_id)
        clock.set(clock.now() + timedelta(hours=2))
        paused = build_dashboard_view(store, clock.now()).timer
        today.start_timer(trial_id)
        clock.set(clock.now() + timedelta(minutes=5))
        resumed = build_dashboard_view(store, clock.now()).timer
    assert paused is not None and resumed is not None
    assert (paused.elapsed_s, paused.running) == (600, False)
    assert resumed.elapsed_s == 900


def test_conquering_a_timed_trial_records_the_timed_minutes(
    store: Store, clock: FixedClock
) -> None:
    today = seal_day(store, clock, "A", "B")
    a = by_title(store)["A"]
    today.start_timer(a.id)
    clock.set(clock.now() + timedelta(minutes=31))
    today.conquer(a.id)
    assert by_title(store)["A"].essence_actual_min == 31


def test_reset_clears_the_timer(store: Store, clock: FixedClock) -> None:
    today = seal_day(store, clock, "A")
    a = by_title(store)["A"]
    today.start_timer(a.id)
    clock.set(clock.now() + timedelta(minutes=3))
    today.reset_timer(a.id)
    timer = build_dashboard_view(store, clock.now()).timer
    assert timer is not None
    assert (timer.elapsed_s, timer.running) == (0, False)


def test_only_the_immediate_trial_has_a_timer(store: Store, clock: FixedClock) -> None:
    today = seal_day(store, clock, "A", "B")
    with pytest.raises(TrialError, match="Immediate"):
        today.start_timer(by_title(store)["B"].id)


def test_time_worked_goes_to_the_horizon_and_comes_back_when_summoned(
    store: Store, clock: FixedClock
) -> None:
    today = seal_day(store, clock, "A")
    a = by_title(store)["A"]
    today.start_timer(a.id)
    clock.set(clock.now() + timedelta(minutes=12))
    today.postpone(a.id)
    (item,) = store.horizon.list_all()
    assert item.worked_s == 12 * 60

    today.summon("horizon", item.id)
    back = build_dashboard_view(store, clock.now()).timer
    assert back is not None
    assert (back.elapsed_s, back.running) == (12 * 60, False)

    today.start_timer(by_title(store)["A"].id)
    clock.set(clock.now() + timedelta(minutes=8))
    today.conquer(by_title(store)["A"].id)
    assert by_title(store)["A"].essence_actual_min == 20
