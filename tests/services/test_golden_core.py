from datetime import date

import pytest

from scrolly.clock import FixedClock
from scrolly.domain.models import Art, ArtKind, Day, PlanStatus, TrialState
from scrolly.domain.planning import PlanningError
from scrolly.domain.qi import QiError
from scrolly.ports import Store
from scrolly.services.golden_core import GoldenCoreService, build_qi_view
from scrolly.services.planning_view import build_planning_view
from tests.factories import DAY, make_trial
from tests.services.flow import Flow


@pytest.fixture
def flow(store: Store, clock: FixedClock) -> Flow:
    return Flow(store, clock)


def _to_estimate(flow: Flow, *, golden_core: bool) -> None:
    if golden_core:
        GoldenCoreService(flow.store, flow.clock).set_enabled(True)
    flow.planning.start()
    flow.planning.save_text("Write report\nTidy desk")
    flow.planning.proceed()


def test_the_golden_core_is_off_and_uninvited_by_default(flow: Flow) -> None:
    setting = GoldenCoreService(flow.store, flow.clock).setting()
    assert (setting.enabled, setting.invited) == (False, False)


def test_either_answer_retires_the_invitation(flow: Flow) -> None:
    service = GoldenCoreService(flow.store, flow.clock)
    service.set_enabled(False)
    assert (service.setting().enabled, service.setting().invited) == (False, True)
    service.set_enabled(True)
    assert (service.setting().enabled, service.setting().invited) == (True, True)


def test_with_the_golden_core_off_proceed_stops_at_estimate_and_seal_stores_no_qi(
    flow: Flow,
) -> None:
    _to_estimate(flow, golden_core=False)
    with pytest.raises(PlanningError):
        flow.planning.proceed()
    flow.planning.seal()
    assert flow.store.days.get(DAY).qi_start is None  # type: ignore[union-attr]


def test_with_the_golden_core_on_estimate_leads_to_weigh_and_back(flow: Flow) -> None:
    _to_estimate(flow, golden_core=True)
    flow.planning.proceed()
    assert flow.status() is PlanStatus.WEIGH
    flow.planning.back()
    assert flow.status() is PlanStatus.ESTIMATE


def test_the_scroll_cannot_be_sealed_without_weighing_first(flow: Flow) -> None:
    _to_estimate(flow, golden_core=True)
    with pytest.raises(PlanningError):
        flow.planning.seal()


def test_sealing_stores_the_suggested_start_unless_the_user_slid_it(flow: Flow) -> None:
    _to_estimate(flow, golden_core=True)
    flow.planning.proceed()
    flow.planning.set_qi_start(40)
    flow.planning.seal()
    assert flow.store.days.get(DAY).qi_start == 40  # type: ignore[union-attr]


def test_the_default_start_is_100(flow: Flow) -> None:
    _to_estimate(flow, golden_core=True)
    flow.planning.proceed()
    flow.planning.seal()
    assert flow.store.days.get(DAY).qi_start == 100  # type: ignore[union-attr]


def test_a_start_outside_the_range_is_refused(flow: Flow) -> None:
    _to_estimate(flow, golden_core=True)
    flow.planning.proceed()
    with pytest.raises(QiError):
        flow.planning.set_qi_start(101)
    with pytest.raises(QiError):
        flow.planning.set_qi_start(5)


def test_switching_the_golden_core_off_while_weighing_steps_back(flow: Flow) -> None:
    _to_estimate(flow, golden_core=True)
    flow.planning.proceed()
    GoldenCoreService(flow.store, flow.clock).set_enabled(False)
    assert flow.status() is PlanStatus.ESTIMATE


def test_qi_is_set_per_trial_and_a_blank_clears_it(flow: Flow) -> None:
    _to_estimate(flow, golden_core=True)
    (first, _second) = build_planning_view(flow.store, DAY).trials
    flow.scroll.update(first.id, None, None, "35")
    assert build_planning_view(flow.store, DAY).trials[0].qi_expected == 35
    flow.scroll.update(first.id, None, None, "")
    assert build_planning_view(flow.store, DAY).trials[0].qi_expected is None
    with pytest.raises(QiError):
        flow.scroll.update(first.id, None, None, "101")


def test_an_art_copy_carries_its_qi(flow: Flow) -> None:
    flow.store.arts.save(
        [Art("art-1", ArtKind.RESTORATIVE, "Meditate", 20, qi_expected=25)], flow.clock.now()
    )
    flow.planning.start()
    flow.scroll.summon("art", "art-1")
    assert build_planning_view(flow.store, DAY).trials[0].qi_expected == 25


def _yesterday(flow: Flow, start: int, spent: int) -> None:
    past = date(2026, 10, 17)
    now = flow.clock.now()
    flow.store.days.save(Day(logical_day=past, first_sealed_at=now, qi_start=start), now)
    flow.store.trials.save(
        [make_trial("hard", logical_day=past, state=TrialState.DONE, qi_expected=spent)], now
    )


def test_a_hard_yesterday_lowers_todays_start(flow: Flow) -> None:
    _yesterday(flow, 100, 130)
    qi = build_qi_view(flow.store, flow.clock.now())
    assert (qi.start, qi.low, qi.high, qi.redline) == (70, 10, 70, 170)


def test_a_day_past_the_redline_leaves_exactly_10_and_no_override(flow: Flow) -> None:
    _yesterday(flow, 100, 100)  # a trial costs at most 100, so more trials make 201 in all
    now = flow.clock.now()
    past = date(2026, 10, 17)
    more = [
        make_trial(name, logical_day=past, state=TrialState.DONE, qi_expected=qi)
        for name, qi in (("more", 100), ("extra", 1))
    ]
    flow.store.trials.save(more, now)
    qi = build_qi_view(flow.store, now)
    assert (qi.start, qi.low, qi.high) == (10, 10, 10)


def test_unused_qi_gives_the_next_day_a_bonus(flow: Flow) -> None:
    _yesterday(flow, 100, 90)
    assert build_qi_view(flow.store, flow.clock.now()).start == 110


def test_the_view_previews_tomorrow_from_the_plan(flow: Flow) -> None:
    _to_estimate(flow, golden_core=True)
    for trial in build_planning_view(flow.store, DAY).trials:
        flow.scroll.update(trial.id, None, None, "100")
    qi = build_qi_view(flow.store, flow.clock.now())
    assert (qi.planned, qi.tomorrow_start) == (200, 10)
