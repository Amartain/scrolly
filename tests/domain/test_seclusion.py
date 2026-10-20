from scrolly.domain.seclusion import (
    IncenseState,
    IncenseView,
    incense_view,
    ring_elapsed,
    seconds_to_gong,
)

ESTIMATE = 45 * 60


def test_before_the_estimate_the_ring_counts_down() -> None:
    assert incense_view(27 * 60, ESTIMATE) == IncenseView(IncenseState.REMAINING, 18 * 60, 0)


def test_past_the_estimate_it_is_overfilled_and_counts_up() -> None:
    assert incense_view(ESTIMATE + 60, ESTIMATE) == IncenseView(IncenseState.OVERFILLED, 0, 60)


def test_at_the_estimate_it_is_overfilled_by_nothing() -> None:
    assert incense_view(ESTIMATE, ESTIMATE) == IncenseView(IncenseState.OVERFILLED, 0, 0)


def test_the_gong_sounds_at_the_estimate_then_every_thirty_minutes() -> None:
    assert seconds_to_gong(0, ESTIMATE) == ESTIMATE
    assert seconds_to_gong(ESTIMATE - 1, ESTIMATE) == 1
    assert seconds_to_gong(ESTIMATE + 1, ESTIMATE) == 30 * 60 - 1
    assert seconds_to_gong(ESTIMATE + 30 * 60 - 1, ESTIMATE) == 1
    assert seconds_to_gong(ESTIMATE + 30 * 60 + 5, ESTIMATE) == 30 * 60 - 5


def test_new_timer_and_zero_out_count_from_the_time_already_logged() -> None:
    assert ring_elapsed(27 * 60, baseline_s=20 * 60) == 7 * 60
    assert ring_elapsed(27 * 60) == 27 * 60


def test_a_baseline_above_the_logged_time_is_ignored_after_a_reset() -> None:
    assert ring_elapsed(5 * 60, baseline_s=20 * 60) == 5 * 60
