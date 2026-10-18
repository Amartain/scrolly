from datetime import date, datetime

import pytest

from scrolly.clock import FixedClock
from scrolly.domain.models import PlanStatus
from scrolly.ports import Store
from scrolly.services.day import DayService
from scrolly.services.planning import PlanningService
from scrolly.services.planning_view import build_planning_view
from scrolly.storage.store import SqliteStores
from tests.factories import DAY, make_item, make_trial
from tests.services.flow import Flow


@pytest.fixture
def flow(store: Store, clock: FixedClock) -> Flow:
    return Flow(store, clock)


def _plan_two_lines(flow: Flow) -> None:
    flow.planning.start()
    flow.planning.save_text("Write report\n\nTidy desk\n")
    flow.planning.proceed()


def test_a_draft_survives_a_new_store(stores: SqliteStores, clock: FixedClock) -> None:
    with stores() as first:
        PlanningService(first, clock).start()
        PlanningService(first, clock).save_text("typed before the reload")
    with stores() as second:
        assert build_planning_view(second, DAY).text == "typed before the reload"


def test_a_stale_draft_is_abandoned_at_rollover_not_lost_to_time(
    store: Store, clock: FixedClock
) -> None:
    store.horizon.replace_all([make_item("Plan", id="h1", is_mandate=True)], clock.now())
    flow = Flow(store, clock)
    flow.planning.start()
    flow.scroll.summon("horizon", "h1")
    flow.planning.save_text("a line")
    flow.planning.proceed()
    clock.set(datetime.fromisoformat("2026-10-19T04:00:00+02:00"))
    DayService(store, clock).ensure_today()
    assert store.drafts.get() is None
    assert store.trials.list_for_day(DAY) == []
    assert [i.id for i in store.horizon.list_all()] == ["h1"]
    assert build_planning_view(store, date(2026, 10, 19)).status is PlanStatus.ZERO


def test_a_sealed_day_is_kept_when_a_draft_is_left_behind(store: Store, clock: FixedClock) -> None:
    flow = Flow(store, clock)
    _plan_two_lines(flow)
    flow.planning.seal()
    store.trials.save([make_trial("late import", id="x")], clock.now())
    flow.planning.start()  # a leftover draft on a sealed day
    clock.set(datetime.fromisoformat("2026-10-19T04:00:00+02:00"))
    DayService(store, clock).ensure_today()
    assert store.drafts.get() is None
    assert any(t.id == "x" or t.title == "late import" for t in store.trials.list_all())
