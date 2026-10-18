from datetime import datetime


class SystemClock:
    """The one source of "now" in production: aware, local time zone."""

    def now(self) -> datetime:
        return datetime.now().astimezone()


class FixedClock:
    """A clock that returns the same moment until moved. For tests."""

    def __init__(self, now: datetime) -> None:
        self._now = now

    def now(self) -> datetime:
        return self._now

    def set(self, now: datetime) -> None:
        self._now = now
