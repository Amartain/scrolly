from datetime import timedelta

from scrolly.clock import FixedClock
from scrolly.domain.models import TrialState
from scrolly.domain.segments import Discipline
from scrolly.ports import Store
from scrolly.services.day import DayService
from scrolly.services.seclusion_state import KEY
from tests.factories import DAY
from tests.services.flow import by_title, seal_day


def _segments(store: Store, trial_id: str):  # type: ignore[no-untyped-def]
    return store.segments.list_for_trial(trial_id)


def test_start_and_pause_write_one_closed_segment(store: Store, clock: FixedClock) -> None:
    today = seal_day(store, clock, "A")
    trial_id = by_title(store)["A"].id
    today.start_timer(trial_id)
    start = clock.now()
    clock.set(start + timedelta(minutes=10))
    today.pause_timer(trial_id)
    (segment,) = _segments(store, trial_id)
    assert (segment.discipline, segment.started_at, segment.ended_at) == (
        Discipline.DASHBOARD,
        start,
        start + timedelta(minutes=10),
    )


def test_a_second_start_while_running_does_not_open_another_segment(
    store: Store, clock: FixedClock
) -> None:
    today = seal_day(store, clock, "A")
    trial_id = by_title(store)["A"].id
    today.start_timer(trial_id)
    today.start_timer(trial_id)
    assert len(_segments(store, trial_id)) == 1


def test_conquering_closes_the_running_segment(store: Store, clock: FixedClock) -> None:
    today = seal_day(store, clock, "A", "B")
    trial_id = by_title(store)["A"].id
    today.start_timer(trial_id)
    today.conquer(trial_id)
    assert store.segments.list_open() == []


def test_switching_trials_closes_the_segment_of_the_one_that_was_running(
    store: Store, clock: FixedClock
) -> None:
    today = seal_day(store, clock, "A", "B")
    trials = by_title(store)
    today.start_timer(trials["A"].id)
    today.promote(trials["B"].id)
    assert store.segments.list_open() == []


def test_reset_removes_the_trials_segments(store: Store, clock: FixedClock) -> None:
    today = seal_day(store, clock, "A")
    trial_id = by_title(store)["A"].id
    today.start_timer(trial_id)
    today.reset_timer(trial_id)
    assert _segments(store, trial_id) == []


def test_abandoning_after_twenty_minutes_adds_them_to_the_essence_spent(
    store: Store, clock: FixedClock
) -> None:
    today = seal_day(store, clock, "A", "B")
    trial_id = by_title(store)["A"].id
    today.start_timer(trial_id)
    clock.set(clock.now() + timedelta(minutes=20))
    today.abandon(trial_id)
    assert by_title(store)["A"].essence_actual_min == 20


def _hold_seclusion(store: Store, clock: FixedClock) -> None:
    store.settings.set(KEY, {"active": True, "day": DAY.isoformat()}, clock.now())


def test_the_scroll_open_in_seclusion_survives_the_rollover_and_is_worked_on(
    store: Store, clock: FixedClock
) -> None:
    today = seal_day(store, clock, "A", "B")
    trials = by_title(store)
    today.start_timer(trials["A"].id)
    _hold_seclusion(store, clock)
    clock.set(clock.now().replace(day=19, hour=4, minute=30))
    DayService(store, clock).ensure_today()
    assert by_title(store)["A"].state is TrialState.IMMEDIATE
    assert by_title(store)["A"].timer_started_at is not None
    today.conquer(trials["A"].id)
    assert by_title(store)["A"].state is TrialState.DONE
    assert by_title(store)["B"].state is TrialState.IMMEDIATE


def test_leaving_seclusion_lets_the_held_scroll_roll_over_and_closes_its_segment(
    store: Store, clock: FixedClock
) -> None:
    today = seal_day(store, clock, "A", "B")
    trials = by_title(store)
    today.start_timer(trials["A"].id)
    _hold_seclusion(store, clock)
    clock.set(clock.now().replace(day=19, hour=4, minute=30))
    DayService(store, clock).ensure_today()
    store.settings.set(KEY, {"active": False, "day": DAY.isoformat()}, clock.now())
    from scrolly.services.day import run_rollover

    run_rollover(store, clock.now().date(), clock.now())
    assert {t.state for t in by_title(store).values()} == {TrialState.LOST}
    assert store.segments.list_open() == []
