from datetime import date, datetime, timedelta

from scrolly.domain.models import Day
from scrolly.domain.planning_timer import close_at, elapsed_seconds, is_running, pause, reset, start

NOW = datetime.fromisoformat("2026-10-18T10:00:00+02:00")
DAY = Day(logical_day=date(2026, 10, 18))


def test_a_new_day_has_no_planning_time() -> None:
    assert elapsed_seconds(DAY, NOW) == 0 and not is_running(DAY)


def test_the_time_is_worked_out_from_the_start_not_counted() -> None:
    running = start(DAY, NOW)
    assert is_running(running)
    assert elapsed_seconds(running, NOW + timedelta(minutes=7, seconds=3)) == 423
    # A long gap (a closed tab, a sleeping laptop) loses nothing.
    assert elapsed_seconds(running, NOW + timedelta(hours=2)) == 7200


def test_pausing_keeps_the_total_and_a_second_stretch_adds() -> None:
    first = pause(start(DAY, NOW), NOW + timedelta(minutes=5))
    assert (first.planning_started_at, first.planning_accumulated_s) == (None, 300)
    later = pause(start(first, NOW + timedelta(hours=3)), NOW + timedelta(hours=3, minutes=2))
    assert later.planning_accumulated_s == 420


def test_starting_twice_keeps_the_first_start_and_pausing_twice_changes_nothing() -> None:
    once = start(DAY, NOW)
    assert start(once, NOW + timedelta(minutes=1)) == once
    stopped = pause(once, NOW + timedelta(minutes=1))
    assert pause(stopped, NOW + timedelta(minutes=9)) == stopped


def test_a_reset_zeroes_it_even_while_running() -> None:
    running = start(replace_total(DAY, 900), NOW)
    zeroed = reset(running)
    assert (zeroed.planning_started_at, zeroed.planning_accumulated_s) == (None, 0)


def test_a_timer_left_running_stops_at_the_end_of_its_day() -> None:
    evening = datetime.fromisoformat("2026-10-18T23:30:00+02:00")
    end = datetime.fromisoformat("2026-10-19T04:00:00+02:00")
    closed = close_at(start(DAY, evening), end)
    assert closed.planning_accumulated_s == 4 * 3600 + 30 * 60 and not is_running(closed)


def replace_total(day: Day, seconds: int) -> Day:
    from dataclasses import replace

    return replace(day, planning_accumulated_s=seconds)
