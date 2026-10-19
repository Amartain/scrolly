import re

MAX_MINUTES = 16 * 60
HINT = "Use 45m, 2h or 1h30m"

_HOURS_MINUTES = re.compile(r"(?:([0-9]+)h)?(?:([0-9]+)m)?")


class DurationError(ValueError):
    """A time that cannot be used. The message is the hint shown to the user."""


def parse_duration(text: str) -> int | None:
    """Minutes from "45m", "2h" or "1h30m" (spaces and case ignored), or blank (None).

    The units are required, minutes are 0-59 next to hours, and the total is 1 minute to 16 hours.
    """
    cleaned = "".join(text.split()).lower()
    if not cleaned:
        return None
    match = _HOURS_MINUTES.fullmatch(cleaned)
    if match is None or not any(match.groups()):
        raise DurationError(HINT)
    hours, minutes = match.groups()
    if hours is not None and minutes is not None and int(minutes) > 59:
        raise DurationError(HINT)
    total = int(hours or 0) * 60 + int(minutes or 0)
    if not 1 <= total <= MAX_MINUTES:
        raise DurationError(HINT)
    return total


def format_duration(minutes: int) -> str:
    """The inverse of parse_duration: "45m", "2h", "1h15m"."""
    hours, rest = divmod(minutes, 60)
    if hours == 0:
        return f"{rest}m"
    return f"{hours}h" if rest == 0 else f"{hours}h{rest}m"
