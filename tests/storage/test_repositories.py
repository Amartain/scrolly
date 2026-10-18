from dataclasses import replace
from datetime import date, datetime

from scrolly.clock import FixedClock
from scrolly.domain.models import Art, ArtKind, Day, OriginType, TrialState
from scrolly.ports import Store
from tests.factories import make_item, make_trial


def test_a_trial_survives_a_round_trip_including_timer_and_times(
    store: Store, clock: FixedClock
) -> None:
    moment = datetime.fromisoformat("2026-10-18T09:00:00+02:00")
    trial = make_trial(
        "Walk",
        state=TrialState.DONE,
        is_mandate=True,
        origin_type=OriginType.HORIZON,
        origin_id="h1",
        essence_expected_min=30,
        essence_actual_min=41,
        completed_at=moment,
        note="note",
        timer_paused_at=moment,
        timer_accumulated_s=2460,
    )
    store.trials.save([trial], clock.now())
    assert store.trials.list_all() == [trial]


def test_saving_again_updates_instead_of_adding(store: Store, clock: FixedClock) -> None:
    trial = make_trial("Walk")
    store.trials.save([trial], clock.now())
    store.trials.save([replace(trial, title="Long walk")], clock.now())
    assert [t.title for t in store.trials.list_all()] == ["Long walk"]


def test_open_before_returns_only_open_trials_of_earlier_days(
    store: Store, clock: FixedClock
) -> None:
    past = date(2026, 10, 15)
    store.trials.save(
        [
            make_trial("old open", logical_day=past),
            make_trial("old done", logical_day=past, state=TrialState.DONE),
            make_trial("today"),
        ],
        clock.now(),
    )
    titles = [t.title for t in store.trials.list_open_before(date(2026, 10, 18))]
    assert titles == ["old open"]


def test_the_horizon_is_stored_in_order_and_replace_removes_the_rest(
    store: Store, clock: FixedClock
) -> None:
    a, b, c = make_item("A"), make_item("B"), make_item("C")
    store.horizon.replace_all([a, b, c], clock.now())
    store.horizon.replace_all([c, a], clock.now())
    assert store.horizon.list_all() == [c, a]


def test_arts_keep_their_order_and_new_ones_go_last(store: Store, clock: FixedClock) -> None:
    first = Art(id="1", kind=ArtKind.FOUNDATIONAL, title="One")
    second = Art(id="2", kind=ArtKind.RESTORATIVE, title="Two", essence_expected_min=10)
    store.arts.save([first], clock.now())
    store.arts.save([second], clock.now())
    assert store.arts.list_all() == [first, second]


def test_a_day_is_found_by_its_logical_day_and_updated_in_place(
    store: Store, clock: FixedClock
) -> None:
    day = Day(logical_day=date(2026, 10, 18))
    assert store.days.get(day.logical_day) is None
    store.days.save(day, clock.now())
    store.days.save(replace(day, first_sealed_at=clock.now(), advisor_silenced=True), clock.now())
    (stored,) = store.days.list_all()
    assert stored.first_sealed_at == clock.now() and stored.advisor_silenced
