from scrolly.domain.essence import EssenceBar, EssenceSummary, essence_bar


def summary(actual: int, remaining: int) -> EssenceSummary:
    return EssenceSummary(actual, actual + remaining, remaining, 0)


def test_the_light_reaching_further_sets_the_scale() -> None:
    # 1h done, 1h still planned, 2h of light: the plan ends at 2h of a 3h scale.
    bar = essence_bar(summary(60, 60), light_left_min=120)
    assert bar == EssenceBar(done_pct=33.33, plan_pct=66.67, sunset_pct=100.0)


def test_a_plan_past_the_sunset_sets_the_scale_and_the_mark_falls_inside() -> None:
    bar = essence_bar(summary(60, 180), light_left_min=60)
    assert bar == EssenceBar(done_pct=25.0, plan_pct=100.0, sunset_pct=50.0)


def test_no_sunset_or_after_it_there_is_no_mark() -> None:
    bar = essence_bar(summary(30, 90), light_left_min=None)
    assert bar == EssenceBar(done_pct=25.0, plan_pct=100.0, sunset_pct=None)


def test_an_empty_day_is_all_zero_and_never_divides_by_zero() -> None:
    assert essence_bar(summary(0, 0), light_left_min=None) == EssenceBar(0.0, 0.0, None)
