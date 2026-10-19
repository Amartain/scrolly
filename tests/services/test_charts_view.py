from scrolly.clock import FixedClock
from scrolly.domain.analytics import Metric
from scrolly.ports import Store
from scrolly.services.dashboard_view import build_dashboard_view
from scrolly.services.golden_core import GoldenCoreService
from tests.factories import DAY
from tests.services.flow import by_title, seal_day


def _charts(store: Store, clock: FixedClock) -> dict[Metric, tuple[bool, int]]:
    charts = build_dashboard_view(store, clock.now()).charts
    return {c.metric: (c.placeholder, len(c.momentum)) for c in charts}


def test_a_fresh_scroll_shows_placeholders_for_trials_and_essence(
    store: Store, clock: FixedClock
) -> None:
    seal_day(store, clock, "Walk")
    charts = _charts(store, clock)
    assert set(charts) == {Metric.TRIALS, Metric.ESSENCE}
    assert all(placeholder for placeholder, _ in charts.values())


def test_conquering_turns_the_trials_chart_real(store: Store, clock: FixedClock) -> None:
    today = seal_day(store, clock, "Walk", "Read")
    today.conquer(by_title(store)["Walk"].id)
    view = build_dashboard_view(store, clock.now())
    trials = next(c for c in view.charts if c.metric is Metric.TRIALS)
    assert not trials.placeholder
    assert [(p.day, p.value) for p in trials.momentum] == [(DAY, 1)]
    assert trials.rhythm[-1].value == 1 and not trials.rhythm[-1].is_rest
    assert all(b.is_rest for b in trials.rhythm[:-1])


def test_a_revived_trial_leaves_the_chart(store: Store, clock: FixedClock) -> None:
    today = seal_day(store, clock, "Walk", "Read")
    walk = by_title(store)["Walk"]
    today.conquer(walk.id)
    today.revive(walk.id)
    assert _charts(store, clock)[Metric.TRIALS][0] is True


def test_qi_joins_the_toggle_only_with_the_golden_core(store: Store, clock: FixedClock) -> None:
    seal_day(store, clock, "Walk")
    GoldenCoreService(store, clock).set_enabled(True)
    assert Metric.QI in _charts(store, clock)
    GoldenCoreService(store, clock).set_enabled(False)
    assert Metric.QI not in _charts(store, clock)
