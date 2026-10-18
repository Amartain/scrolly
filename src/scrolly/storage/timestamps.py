from datetime import UTC, datetime


def utc_iso(moment: datetime) -> str:
    return moment.astimezone(UTC).isoformat()


def from_iso(text: str | None) -> datetime | None:
    return None if text is None else datetime.fromisoformat(text)
