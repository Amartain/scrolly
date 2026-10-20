from datetime import date, datetime, time, timedelta

ROLLOVER_HOUR = 4


def logical_day(now: datetime) -> date:
    """The day a moment belongs to. 00:00-03:59 still counts as the previous day."""
    return (now - timedelta(hours=ROLLOVER_HOUR)).date()


def logical_day_end(day: date, like: datetime) -> datetime:
    """When a logical day ends: the 04:00 that begins the next one, in the time zone of `like`."""
    return datetime.combine(day + timedelta(days=1), time(ROLLOVER_HOUR), tzinfo=like.tzinfo)
