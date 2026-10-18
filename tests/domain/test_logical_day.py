from datetime import UTC, date, datetime, timedelta

from hypothesis import given
from hypothesis import strategies as st

from scrolly.domain.logical_day import logical_day


def test_before_four_belongs_to_previous_day() -> None:
    assert logical_day(datetime(2026, 10, 18, 3, 59)) == date(2026, 10, 17)


def test_four_oclock_starts_the_new_day() -> None:
    assert logical_day(datetime(2026, 10, 18, 4, 0)) == date(2026, 10, 18)


def test_midnight_is_still_the_previous_day() -> None:
    assert logical_day(datetime(2026, 10, 18, 0, 0)) == date(2026, 10, 17)


def test_year_and_month_edges() -> None:
    assert logical_day(datetime(2027, 1, 1, 2, 0)) == date(2026, 12, 31)
    assert logical_day(datetime(2026, 3, 1, 1, 0)) == date(2026, 2, 28)


@given(st.datetimes(min_value=datetime(2000, 1, 2), timezones=st.just(UTC)))
def test_is_the_date_four_hours_earlier(moment: datetime) -> None:
    assert logical_day(moment) == (moment - timedelta(hours=4)).date()
