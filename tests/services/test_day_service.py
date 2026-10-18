from datetime import date, datetime

from scrolly.clock import FixedClock
from scrolly.domain.models import TrialState
from scrolly.ports import Store
from scrolly.services.day import DayService
from tests.factories import make_trial

THURSDAY = date(2026, 10, 15)


def _seed(store: Store, clock: FixedClock) -> None:
    now = clock.now()
    store.trials.save(
        [
            make_trial("Walk", id="m", logical_day=THURSDAY),
            make_trial("Taxes", id="t", logical_day=THURSDAY, is_mandate=True),
            make_trial("Done", id="d", logical_day=THURSDAY, state=TrialState.DONE),
        ],
        now,
    )


def _states(store: Store) -> dict[str, TrialState]:
    return {t.id: t.state for t in store.trials.list_all()}


def test_the_first_request_of_a_new_logical_day_rolls_over(store: Store, clock: FixedClock) -> None:
    _seed(store, clock)
    DayService(store, clock).ensure_today()
    assert _states(store) == {
        "m": TrialState.LOST,
        "t": TrialState.RETURNED,
        "d": TrialState.DONE,
    }
    assert [item.title for item in store.horizon.list_all()] == ["Taxes"]


def test_rollover_runs_once_per_logical_day(store: Store, clock: FixedClock) -> None:
    _seed(store, clock)
    service = DayService(store, clock)
    service.ensure_today()
    store.trials.save([make_trial("Late", id="late", logical_day=THURSDAY)], clock.now())
    service.ensure_today()
    assert _states(store)["late"] is TrialState.REMAINING  # today's row is already rolled over


def test_before_four_in_the_morning_it_is_still_the_old_day(
    store: Store, clock: FixedClock
) -> None:
    clock.set(datetime.fromisoformat("2026-10-16T03:59:00+02:00"))
    _seed(store, clock)
    DayService(store, clock).ensure_today()
    assert set(_states(store).values()) == {TrialState.REMAINING, TrialState.DONE}
    clock.set(datetime.fromisoformat("2026-10-16T04:00:00+02:00"))
    DayService(store, clock).ensure_today()
    assert _states(store)["m"] is TrialState.LOST
