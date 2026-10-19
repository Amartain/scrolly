from datetime import datetime, timedelta

from scrolly.domain.timer import actual_minutes, elapsed_seconds, pause, reset, start
from tests.factories import make_trial

NOW = datetime.fromisoformat("2026-10-18T13:00:00+02:00")


def test_a_stopped_timer_shows_its_accumulated_time() -> None:
    assert elapsed_seconds(make_trial(timer_accumulated_s=300), NOW) == 300


def test_a_running_timer_adds_the_open_segment() -> None:
    trial = make_trial(timer_accumulated_s=300, timer_started_at=NOW - timedelta(seconds=90))
    assert elapsed_seconds(trial, NOW) == 390


def test_a_clock_that_moved_back_never_gives_negative_time() -> None:
    trial = make_trial(timer_started_at=NOW + timedelta(seconds=30))
    assert elapsed_seconds(trial, NOW) == 0


def test_pause_folds_the_segment_into_the_total() -> None:
    trial = make_trial(timer_accumulated_s=300, timer_started_at=NOW - timedelta(seconds=90))
    paused = pause(trial, NOW)
    assert (paused.timer_started_at, paused.timer_paused_at) == (None, NOW)
    assert paused.timer_accumulated_s == 390


def test_pausing_a_stopped_timer_changes_nothing() -> None:
    trial = make_trial(timer_accumulated_s=300)
    assert pause(trial, NOW) == trial


def test_start_then_pause_records_the_time_between_the_two_moments() -> None:
    started = start(make_trial(), NOW)
    paused = pause(started, NOW + timedelta(minutes=25))
    assert paused.timer_accumulated_s == 1500


def test_several_segments_add_up() -> None:
    trial = make_trial()
    for begin in (0, 60):
        trial = start(trial, NOW + timedelta(minutes=begin))
        trial = pause(trial, NOW + timedelta(minutes=begin + 10))
    assert trial.timer_accumulated_s == 1200


def test_a_running_timer_read_hours_later_keeps_counting_with_no_request_in_between() -> None:
    trial = start(make_trial(), NOW)
    assert elapsed_seconds(trial, NOW + timedelta(hours=3)) == 3 * 3600


def test_starting_a_running_timer_changes_nothing() -> None:
    trial = start(make_trial(), NOW)
    assert start(trial, NOW + timedelta(minutes=5)) == trial


def test_start_after_a_pause_clears_the_pause_and_keeps_the_total() -> None:
    paused = pause(start(make_trial(), NOW), NOW + timedelta(minutes=10))
    again = start(paused, NOW + timedelta(minutes=30))
    assert (again.timer_paused_at, again.timer_accumulated_s) == (None, 600)


def test_reset_stops_and_zeroes() -> None:
    trial = start(make_trial(timer_accumulated_s=300), NOW)
    cleared = reset(trial)
    assert (cleared.timer_started_at, cleared.timer_paused_at, cleared.timer_accumulated_s) == (
        None,
        None,
        0,
    )


def test_actual_minutes_from_a_timer_that_ran_rounds_to_the_nearest_minute() -> None:
    trial = start(make_trial(essence_expected_min=45), NOW)
    assert actual_minutes(trial, NOW + timedelta(seconds=25 * 60 + 40)) == 26


def test_a_short_run_still_counts_as_one_minute() -> None:
    trial = start(make_trial(essence_expected_min=45), NOW)
    assert actual_minutes(trial, NOW + timedelta(seconds=10)) == 1


def test_actual_minutes_without_a_timer_is_the_estimate_or_nothing() -> None:
    assert actual_minutes(make_trial(essence_expected_min=45), NOW) == 45
    assert actual_minutes(make_trial(), NOW) is None
