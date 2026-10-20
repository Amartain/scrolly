from datetime import date, timedelta
from itertools import pairwise

from hypothesis import given
from hypothesis import strategies as st

from scrolly.domain.analytics import (
    Metric,
    daily_totals,
    momentum,
    placeholder_momentum,
    placeholder_rhythm,
    rhythm,
    thin,
)
from scrolly.domain.models import Trial, TrialState
from tests.factories import make_trial

TODAY = date(2026, 10, 19)


def done(day: date, *, minutes: int | None = None, qi: int | None = None, key: str = "") -> Trial:
    return make_trial(
        f"t-{day}-{key}",
        state=TrialState.DONE,
        logical_day=day,
        essence_actual_min=minutes,
        qi_expected=qi,
    )


def test_momentum_is_a_running_total_over_the_days_that_rose() -> None:
    trials = [
        done(date(2026, 10, 1), key="a"),
        done(date(2026, 10, 1), key="b"),
        done(date(2026, 10, 5), key="c"),
        make_trial("open", logical_day=date(2026, 10, 3)),
    ]
    points = momentum(trials, Metric.TRIALS)
    assert [(p.day, p.value) for p in points] == [(date(2026, 10, 1), 2), (date(2026, 10, 5), 3)]


def test_momentum_of_essence_skips_days_with_no_minutes() -> None:
    trials = [
        done(date(2026, 10, 1), minutes=30),
        done(date(2026, 10, 2)),
        done(date(2026, 10, 3), minutes=45),
    ]
    points = momentum(trials, Metric.ESSENCE)
    assert [(p.day.day, p.value) for p in points] == [(1, 30), (3, 75)]


def test_momentum_of_qi_adds_what_was_recorded() -> None:
    trials = [done(date(2026, 10, 1), qi=20), done(date(2026, 10, 2), qi=15)]
    assert [p.value for p in momentum(trials, Metric.QI)] == [20, 35]


def test_a_revived_trial_does_not_count() -> None:
    assert momentum([make_trial("x", state=TrialState.REMAINING)], Metric.TRIALS) == []


def test_rhythm_covers_the_last_seven_days_and_marks_rest() -> None:
    trials = [done(TODAY, key="a"), done(TODAY - timedelta(days=2), key="b")]
    bars = rhythm(trials, TODAY, Metric.TRIALS)
    assert [b.day for b in bars] == [TODAY - timedelta(days=6 - i) for i in range(7)]
    assert [b.is_rest for b in bars] == [True, True, True, True, False, True, False]
    assert all(b.height_pct == 0 for b in bars if b.is_rest)


def test_one_outstanding_day_does_not_dwarf_the_rest() -> None:
    trials = [done(TODAY, minutes=600)]
    trials += [done(TODAY - timedelta(days=i), minutes=10) for i in range(1, 4)]
    bars = rhythm(trials, TODAY, Metric.ESSENCE)
    heights = [b.height_pct for b in bars if not b.is_rest]
    assert max(heights) == 100
    assert min(heights) >= 25
    assert sorted(heights)[0] > 100 * 10 / 600 * 2  # far taller than a straight scale


def test_equal_days_are_equally_tall() -> None:
    trials = [done(TODAY - timedelta(days=i), key="a") for i in range(3)]
    assert {b.height_pct for b in rhythm(trials, TODAY, Metric.TRIALS) if not b.is_rest} == {100}


def test_the_placeholders_are_fixed_and_well_formed() -> None:
    assert placeholder_momentum(TODAY) == placeholder_momentum(TODAY)
    values = [p.value for p in placeholder_momentum(TODAY)]
    assert values == sorted(set(values)) and len(values) >= 8
    bars = placeholder_rhythm(TODAY)
    assert (
        len(bars) == 7 and any(b.is_rest for b in bars) and max(b.height_pct for b in bars) == 100
    )


def test_thinning_keeps_the_first_and_last_point_and_stays_rising() -> None:
    points = momentum([done(TODAY - timedelta(days=i), key="a") for i in range(200)], Metric.TRIALS)
    thinned = thin(points, 60)
    assert len(thinned) == 60
    assert thinned[0] == points[0] and thinned[-1] == points[-1]
    assert thin(points[:10], 60) == points[:10]


@given(
    st.lists(st.tuples(st.integers(0, 400), st.integers(0, 500)), max_size=60),
    st.sampled_from([Metric.TRIALS, Metric.ESSENCE]),
)
def test_momentum_always_rises_with_ascending_dates(
    days: list[tuple[int, int]], metric: Metric
) -> None:
    trials = [
        done(TODAY - timedelta(days=d), minutes=m, key=str(i)) for i, (d, m) in enumerate(days)
    ]
    points = momentum(trials, metric)
    assert [p.day for p in points] == sorted({p.day for p in points})
    assert all(a.value < b.value for a, b in pairwise(points))
    thinned = thin(points, 60)
    assert len(thinned) <= 60
    assert all(a.value < b.value for a, b in pairwise(thinned))


@given(st.lists(st.integers(0, 2000), min_size=7, max_size=7))
def test_rhythm_heights_stay_in_range(values: list[int]) -> None:
    trials = [
        done(TODAY - timedelta(days=6 - i), minutes=v, key=str(i))
        for i, v in enumerate(values)
        if v > 0
    ]
    bars = rhythm(trials, TODAY, Metric.ESSENCE)
    assert len(bars) == 7
    for bar in bars:
        assert bar.is_rest == (bar.value == 0)
        assert bar.height_pct == 0 if bar.is_rest else 25 <= bar.height_pct <= 100


def test_essence_counts_abandoned_minutes_but_trials_do_not() -> None:
    day = date(2026, 10, 10)
    trials = [
        make_trial("A", logical_day=day, state=TrialState.DONE, essence_actual_min=30),
        make_trial("B", logical_day=day, state=TrialState.LOST, essence_actual_min=20),
    ]
    assert daily_totals(trials, Metric.ESSENCE) == {day: 50}
    assert daily_totals(trials, Metric.TRIALS) == {day: 1}
