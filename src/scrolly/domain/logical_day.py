from datetime import date, datetime, timedelta

ROLLOVER_HOUR = 4


def logical_day(now: datetime) -> date:
    """The day a moment belongs to. 00:00-03:59 still counts as the previous day."""
    return (now - timedelta(hours=ROLLOVER_HOUR)).date()
