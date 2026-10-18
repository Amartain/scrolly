from datetime import datetime, timedelta

from scrolly.domain.timer import elapsed_seconds, pause
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
