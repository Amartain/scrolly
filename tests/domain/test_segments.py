from datetime import date, datetime, timedelta

from scrolly.domain.segments import Discipline, close_segment, open_segment, seconds_by_day

NIGHT = datetime.fromisoformat("2026-10-18T03:30:00+02:00")


def _segment(start: datetime, minutes: int | None = None):  # type: ignore[no-untyped-def]
    opened = open_segment("s", "t", Discipline.INCENSE, start)
    return opened if minutes is None else close_segment(opened, start + timedelta(minutes=minutes))


def test_a_segment_crossing_four_is_split_between_the_two_days() -> None:
    totals = seconds_by_day([_segment(NIGHT, 50)], NIGHT + timedelta(hours=2))
    assert totals == {date(2026, 10, 17): 30 * 60, date(2026, 10, 18): 20 * 60}


def test_a_running_segment_counts_up_to_now() -> None:
    totals = seconds_by_day([_segment(NIGHT)], NIGHT + timedelta(minutes=10))
    assert totals == {date(2026, 10, 17): 600}


def test_a_segment_inside_one_day_stays_whole() -> None:
    noon = NIGHT.replace(hour=12)
    assert seconds_by_day([_segment(noon, 25)], noon + timedelta(hours=9)) == {
        date(2026, 10, 18): 25 * 60
    }


def test_closing_twice_keeps_the_first_end() -> None:
    first = close_segment(_segment(NIGHT), NIGHT + timedelta(minutes=5))
    again = close_segment(first, NIGHT + timedelta(minutes=50))
    assert again.ended_at == NIGHT + timedelta(minutes=5)


def test_a_clock_that_runs_backwards_never_gives_a_negative_segment() -> None:
    closed = close_segment(_segment(NIGHT), NIGHT - timedelta(minutes=5))
    assert closed.ended_at == NIGHT
